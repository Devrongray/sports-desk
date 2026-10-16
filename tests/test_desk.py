"""Arithmetic and rule checks that need no network. Run: pytest -q"""
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from desk.config import load_config
from desk.reference import spread_sign
from desk.scan import ceil_tick, evaluate, floor_tick, quote_state

CFG = load_config()
RULES, DESK = CFG["rules"], CFG["desk"]
NOW = datetime(2026, 10, 20, 23, 0, tzinfo=timezone.utc)


def contract(**kw):
    base = {"sport": "nhl", "market_class": "TOTAL", "segment": "FIRST_PERIOD", "line": 1.5,
            "event_title": "BUF vs TOR", "question": "Will BUF vs TOR have more than 1.5 goals in the first period?",
            "market_slug": "tsc-nhl-buf-tor-2026-10-20-p1-1pt5", "long_team_name": None,
            "start": pd.Timestamp(NOW + timedelta(minutes=60)), "tick": 0.01, "fee_coefficient": 0.0695, "sides": []}
    base.update(kw)
    return base


def quote(bid, ask, bid_sh=None, ask_sh=None):
    return {"bid": bid, "ask": ask, "bid_shares": bid_sh, "ask_shares": ask_sh, "quote_src": "test", "quote_ts": NOW}


def ref(fair, move=None):
    return {"pin_event_id": "x", "pin_market": "totals_p1", "pin_ts": pd.Timestamp(NOW), "pin_age_min": 3.0,
            "pin_price": 1.8, "fair": fair, "fair_15m_ago": None if move is None else fair - move, "pin_move_15m": move,
            "match_how": "nick", "n_pin_snapshots": 4}


def test_fee_at_50_cents():
    from method.fees import taker_fee
    assert abs(taker_fee(0.5) - 0.017375) < 1e-9          # $1.74 per 100 contracts


def test_oct13_case_taker_is_too_thin_but_a_fine_tick_allows_a_maker_bid():
    # fair 0.60, book 0.56 / 0.574: taker nets +0.9 pt (fee 1.7 pts), below the rule.
    # With a 0.1-cent tick a bid at 0.57 improves the book and keeps 3 pts of edge -> post_bid.
    c = contract(market_class="WINNER", segment="FULL_GAME", line=None, long_team_name="Kraken", tick=0.001)
    r = evaluate(c, quote(0.56, 0.574, 1000, 1000), ref(0.60), RULES, DESK, NOW)
    assert r["quote_state"] == "tight"
    assert r["taker_long_net"] == pytest.approx(0.60 - 0.574 - 0.0695 * 0.574 * 0.426, abs=1e-4)  # stored to 4 dp
    assert r["action"] == "post_bid" and r["post_px"] == pytest.approx(0.57) and r["edge_pts"] == pytest.approx(0.03)
    # With a 1-cent tick the same book leaves no room: fair - margin rounds to 0.56, not above the bid -> pass.
    c["tick"] = 0.01
    r2 = evaluate(c, quote(0.56, 0.574, 1000, 1000), ref(0.60), RULES, DESK, NOW)
    assert r2["action"] == "pass" and r2["maker_bid_px"] is None


def test_wide_period_total_gets_a_maker_bid():
    r = evaluate(contract(), quote(0.56, 0.60), ref(0.60), RULES, DESK, NOW)
    assert r["quote_state"] == "wide"
    assert r["action"] == "post_bid"
    assert r["post_px"] == pytest.approx(0.57)       # fair - 3 pts, one tick above the best bid
    assert r["edge_pts"] == pytest.approx(0.03)
    assert r["size_usd"] == pytest.approx(20.0)
    assert r["contracts"] == pytest.approx(20 / 0.57, abs=0.01)  # stored to 2 dp


def test_wide_quote_already_inside_margin_is_a_pass():
    r = evaluate(contract(), quote(0.56, 0.60), ref(0.585), RULES, DESK, NOW)
    assert r["action"] == "pass"
    assert r["maker_bid_px"] is None and r["maker_ask_px"] is None


def test_unquoted_book_posts_both_sides_possible_picks_one():
    r = evaluate(contract(), quote(0.24, 0.91), ref(0.55), RULES, DESK, NOW)
    assert r["quote_state"] == "unquoted"
    assert r["action"] in ("post_bid", "post_ask")
    assert r["maker_bid_px"] == pytest.approx(0.52) and r["maker_ask_px"] == pytest.approx(0.58)
    assert "unquoted" in r["flags"]


def test_pinnacle_just_moved_is_a_pass():
    r = evaluate(contract(), quote(0.56, 0.60), ref(0.62, move=0.03), RULES, DESK, NOW)
    assert r["action"] == "pass" and "late" in r["reason"]


def test_outside_window_is_watch_with_would_action():
    c = contract(start=pd.Timestamp(NOW + timedelta(hours=10)))
    r = evaluate(c, quote(0.56, 0.60), ref(0.60), RULES, DESK, NOW)
    assert r["action"] == "watch" and r["reason"].startswith("would post_bid")


def test_never_buy_below_ten_cents():
    r = evaluate(contract(), quote(0.03, 0.12), ref(0.09), RULES, DESK, NOW)
    assert r["action"] in ("pass", "watch")


def test_taker_short_when_bid_is_rich():
    # book 0.70 / 0.71 (tight), fair 0.64: selling Yes at 0.70 nets 0.06 - fee
    r = evaluate(contract(), quote(0.70, 0.71, 5000, 5000), ref(0.64), RULES, DESK, NOW)
    assert r["action"] == "take_short"
    assert r["taker_short_net"] == pytest.approx(0.70 - 0.64 - 0.0695 * 0.70 * 0.30, abs=1e-4)


def test_spread_sign_from_slug():
    assert spread_sign("asc-nhl-buf-tor-2026-10-15-p1-pos-0pt5") == 1
    assert spread_sign("asc-mlb-tb-cle-2026-10-15-neg-1pt5") == -1
    assert spread_sign("tsc-nhl-buf-tor-2026-10-15-p1-1pt5") == 0


def test_ticks_and_states():
    assert floor_tick(0.574, 0.01) == pytest.approx(0.57)
    assert ceil_tick(0.571, 0.005) == pytest.approx(0.575)
    assert quote_state(0.51, 0.52, RULES) == "tight"
    assert quote_state(0.56, 0.60, RULES) == "wide"
    assert quote_state(0.24, 0.91, RULES) == "unquoted"
    assert quote_state(None, 0.5, RULES) == "none"


def test_oct9_combo_payout_is_impossible():
    legs = (0.69, 0.56, 0.51)
    independent = legs[0] * legs[1] * legs[2]
    assert 1 / independent == pytest.approx(5.07, abs=0.01)
    assert 1 / min(legs) == pytest.approx(1.96, abs=0.01)     # perfectly correlated upper bound
    assert 1 / 1.20 > 0.83                                     # what a 1.20x payout implies


def test_clv_sign_conventions():
    from method.metrics import clv_points
    assert clv_points(0.57, 0.60, "long") == pytest.approx(0.03)
    assert clv_points(0.63, 0.60, "short") == pytest.approx(0.03)


# --- three-way winner legs (16 Oct 2026) -------------------------------------
# Polymarket US quotes period / first-five / regulation winners as three contracts
# (home / away / tie). PIT@COL first period on 16 Oct: COL 0.41, PIT 0.27, tie 0.31.
# Against the two-way h2h_p1 (tie = push) COL's fair would read ~0.60 and the desk
# would have bid 0.57 on a 0.41 contract. These pin the mapping.

def _fair_frame(rows):
    df = pd.DataFrame(rows)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df


def test_pinnacle_market_key_routes_three_way_segments():
    from desk.reference import pinnacle_market_key
    seg = load_config()["segments"]
    assert pinnacle_market_key({"market_class": "WINNER", "segment": "FULL_GAME"}, seg) == "h2h"
    assert pinnacle_market_key({"market_class": "WINNER", "segment": "FIRST_PERIOD"}, seg) == "h2h_3_way_p1"
    assert pinnacle_market_key({"market_class": "WINNER", "segment": "THIRD_PERIOD"}, seg) == "h2h_3_way_p3"
    assert pinnacle_market_key({"market_class": "WINNER", "segment": "FIRST_FIVE"}, seg) == "h2h_3_way_1st_5_innings"
    assert pinnacle_market_key({"market_class": "WINNER", "segment": "REGULATION"}, seg) == "h2h_3_way"
    assert pinnacle_market_key({"market_class": "TOTAL", "segment": "FIRST_PERIOD"}, seg) == "totals_p1"
    assert pinnacle_market_key({"market_class": "SPREAD", "segment": "FIRST_FIVE"}, seg) == "spreads_1st_5_innings"
    assert pinnacle_market_key({"market_class": "TOTAL", "segment": "REGULATION"}, seg) is None   # winner-only segment
    assert pinnacle_market_key({"market_class": "WINNER", "segment": "NOT_A_SEGMENT"}, seg) is None
    assert pinnacle_market_key({"market_class": "TEAM_TOTAL", "segment": "FULL_GAME"}, seg) is None


def test_config_polls_only_three_way_winner_markets_for_period_legs():
    pm = load_config()["period_markets"]["by_sport"]
    for sport, markets in pm.items():
        for m in markets:
            if m.startswith("h2h_"):
                assert m.startswith("h2h_3_way"), f"{sport}: {m} is the two-way market (tie = push); use h2h_3_way_*"


def test_period_winner_contracts_reference_the_three_way_fair_including_the_tie_leg():
    from desk.reference import contract_reference
    cfg = load_config()
    as_of = datetime(2026, 10, 16, 22, 30, tzinfo=timezone.utc)
    ts = "2026-10-16T22:20:00+00:00"
    # Pinnacle three-way first period, already de-vigged: COL 0.42, PIT 0.27, Draw 0.31;
    # and the two-way h2h_p1 the desk must NOT use: COL 0.61, PIT 0.39.
    fair = _fair_frame([
        {"sport": "nhl", "event_id": "P1", "ts": ts, "market": "h2h_3_way_p1", "point": None, "outcome": "Colorado Avalanche", "price": 2.30, "fair_prob": 0.42},
        {"sport": "nhl", "event_id": "P1", "ts": ts, "market": "h2h_3_way_p1", "point": None, "outcome": "Pittsburgh Penguins", "price": 3.50, "fair_prob": 0.27},
        {"sport": "nhl", "event_id": "P1", "ts": ts, "market": "h2h_3_way_p1", "point": None, "outcome": "Draw", "price": 3.10, "fair_prob": 0.31},
        {"sport": "nhl", "event_id": "P1", "ts": ts, "market": "h2h_p1", "point": None, "outcome": "Colorado Avalanche", "price": 1.60, "fair_prob": 0.61},
        {"sport": "nhl", "event_id": "P1", "ts": ts, "market": "h2h_p1", "point": None, "outcome": "Pittsburgh Penguins", "price": 2.45, "fair_prob": 0.39},
    ])
    matches = pd.DataFrame([{"sport": "nhl", "pm_event_id": "156066", "pin_event_id": "P1", "how": "test", "minutes_apart": 0, "pm_teams": "PIT/COL"}])
    base = {"sport": "nhl", "event_id": "156066", "market_class": "WINNER", "segment": "FIRST_PERIOD", "line": None}
    col = contract_reference({**base, "market_slug": "atc-nhl-pit-col-2026-10-16-p1-col", "long_team_name": "Avalanche"},
                             fair, matches, cfg["segments"], as_of)
    pit = contract_reference({**base, "market_slug": "atc-nhl-pit-col-2026-10-16-p1-pit", "long_team_name": "Penguins"},
                             fair, matches, cfg["segments"], as_of)
    tie = contract_reference({**base, "market_slug": "atc-nhl-pit-col-2026-10-16-p1-draw", "long_team_name": float("nan")},
                             fair, matches, cfg["segments"], as_of)
    assert col["pin_market"] == "h2h_3_way_p1" and col["fair"] == pytest.approx(0.42)
    assert pit["fair"] == pytest.approx(0.27)
    assert tie["fair"] == pytest.approx(0.31) and tie["pin_market"] == "h2h_3_way_p1"
    assert abs(col["fair"] + pit["fair"] + tie["fair"] - 1.0) < 1e-9
    # full-game winner still two-way
    fg_fair = _fair_frame([
        {"sport": "nhl", "event_id": "P1", "ts": ts, "market": "h2h", "point": None, "outcome": "Colorado Avalanche", "price": 1.52, "fair_prob": 0.655},
        {"sport": "nhl", "event_id": "P1", "ts": ts, "market": "h2h", "point": None, "outcome": "Pittsburgh Penguins", "price": 2.90, "fair_prob": 0.345},
    ])
    fg = contract_reference({**base, "segment": "FULL_GAME", "market_slug": "aec-nhl-pit-col-2026-10-16", "long_team_name": "Penguins"},
                            fg_fair, matches, cfg["segments"], as_of)
    assert fg["pin_market"] == "h2h" and fg["fair"] == pytest.approx(0.345)


def test_daily_credit_cap_stops_the_poll(tmp_path):
    import json
    from desk.period_poll import credits_spent_today, run_poll
    cfg = load_config()
    as_of = datetime(2026, 10, 16, 23, 0, tzinfo=timezone.utc)
    day = tmp_path / "data" / "desk_pinnacle" / "2026-10-16"
    day.mkdir(parents=True)
    for i, spent in enumerate([120, 130, 110]):
        (day / f"poll_2026101{i}T000000Z.json").write_text(json.dumps({"credits_spent_est": spent}))
    assert credits_spent_today(tmp_path, as_of) == 360
    import os
    os.environ["ODDS_API_KEY"] = "test-not-a-real-key"
    try:
        out = run_poll(cfg, tmp_path / "nodata", tmp_path, as_of)
    finally:
        del os.environ["ODDS_API_KEY"]
    assert out["skipped"].startswith("daily credit cap")
    assert out["events"] == 0 and out["credits_spent_est"] == 0
    assert (tmp_path / "data" / "desk_pinnacle" / "latest_poll.json").exists()
