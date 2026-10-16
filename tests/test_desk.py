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
