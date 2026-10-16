"""Pinnacle fair price for a Polymarket US contract.

Full-game references come from sports-method's Pinnacle rows (h2h, totals).
Period/half/quarter/inning references come from the desk's own poll of the
Odds API per-event endpoint (totals_p1, spreads_h1, ...). Both are de-vigged
with sports-method's `devig` (additive by default: test (c) found additive,
power and Shin equivalent for two-way markets and multiplicative worse).

Contract conventions (read from live payloads, 14–15 Oct 2026):
    WINNER  the long side's team is the team the Yes contract pays for
    TOTAL   Yes = "more than <line>" = Over at that line
    SPREAD  Yes = long team covers <signed line>; the sign is in the slug
            (...-pos-1pt5 = +1.5, ...-neg-1pt5 = -1.5)
"""
from __future__ import annotations

import math
import re
from datetime import datetime, timedelta

import pandas as pd

from .config import ensure_sports_method

ensure_sports_method()
from method.analysis.compare import pinnacle_fair  # noqa: E402
from method.analysis.match import match_events, nickname, norm, pin_event_table, pm_event_table  # noqa: E402

CLASS_TO_MARKET = {"WINNER": "h2h", "TOTAL": "totals", "SPREAD": "spreads"}
# Polymarket US quotes the winner of these segments as THREE contracts per game
# (home / away / tie: "Will COL win the first period?", "Will the first period be
# tied?"). Their reference is Pinnacle's three-way market (h2h_3_way_p1,
# h2h_3_way_1st_5_innings, ...), never the two-way h2h_p1 / h2h_1st_5_innings,
# where a tie is a push and each team's fair is inflated by 1/(1 - P(tie)):
# 15-20¢ on an NHL period. Full-game NHL/NBA/MLB winners include overtime and
# are two-way on both venues.
THREE_WAY_WINNER_SEGMENTS = {"FIRST_PERIOD", "SECOND_PERIOD", "THIRD_PERIOD", "REGULATION",
                             "FIRST_FIVE", "INNING1", "FIRST_THREE", "FIRST_SEVEN"}
# Segments Polymarket US quotes only as a winner (no totals/spreads at that scope).
WINNER_ONLY_SEGMENTS = {"REGULATION"}
_SIGN = re.compile(r"-(pos|neg)-")
_DRAW = re.compile(r"-(draw|tie)$")


def pinnacle_market_key(c: dict, segments: dict[str, str]) -> str | None:
    """The Odds API market key a contract is referenced against, or None."""
    cls, seg = c.get("market_class"), c.get("segment")
    base = CLASS_TO_MARKET.get(cls)
    if base is None or seg not in segments:
        return None
    if seg in WINNER_ONLY_SEGMENTS and cls != "WINNER":
        return None
    if cls == "WINNER" and seg in THREE_WAY_WINNER_SEGMENTS:
        base = "h2h_3_way"
    return base + segments[seg]


def is_draw_contract(c: dict) -> bool:
    """The tie leg of a three-way winner (slug ends in -draw; no long team)."""
    return bool(_DRAW.search(str(c.get("market_slug") or "")))


def fair_table(pin: pd.DataFrame, method: str = "additive") -> pd.DataFrame:
    """One row per (sport, event_id, ts, market, point, outcome) with fair_prob."""
    if pin is None or pin.empty:
        return pd.DataFrame(columns=["sport", "event_id", "ts", "market", "point", "outcome", "price", "fair_prob",
                                     "home", "away", "commence_time"])
    return pinnacle_fair(pin, method)


def match_table(markets: pd.DataFrame, pin: pd.DataFrame, tolerance_minutes: int = 90) -> pd.DataFrame:
    if markets.empty or pin.empty:
        return pd.DataFrame(columns=["sport", "pm_event_id", "pin_event_id", "how", "minutes_apart", "pm_teams"])
    return match_events(pm_event_table(markets), pin_event_table(pin), tolerance_minutes)


def spread_sign(slug: str | None) -> int:
    m = _SIGN.search(slug or "")
    if not m:
        return 0
    return 1 if m.group(1) == "pos" else -1


def _same_point(a, b, tol: float = 1e-6) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def _draw_rows(rows: pd.DataFrame) -> pd.DataFrame:
    return rows[rows["outcome"].map(norm).isin({"draw", "tie"})]


def _team_rows(rows: pd.DataFrame, team_name: str | None) -> pd.DataFrame:
    if not isinstance(team_name, str) or not team_name.strip():   # None or a pandas NaN
        return rows.iloc[0:0]
    n = norm(team_name)
    sel = rows["outcome"].map(norm) == n
    if not sel.any():
        k = nickname(team_name)
        sel = rows["outcome"].map(nickname) == k
    return rows[sel]


def contract_reference(c: dict, fair: pd.DataFrame, matches: pd.DataFrame, segments: dict[str, str],
                       as_of: datetime, max_age_minutes: float = 60) -> dict | None:
    """Fair Yes probability for one Polymarket US main-line contract row.

    Returns None when there is no Pinnacle reference (no event match, no market
    of that class/segment, no matching line, or the quote is too old).
    """
    market_key = pinnacle_market_key(c, segments)
    if market_key is None:
        return None
    mt = matches[(matches["sport"] == c["sport"]) & (matches["pm_event_id"] == c["event_id"])]
    if mt.empty:
        return None
    pin_event_id = mt.iloc[0]["pin_event_id"]
    rows = fair[(fair["sport"] == c["sport"]) & (fair["event_id"] == pin_event_id) & (fair["market"] == market_key)]
    rows = rows[rows["ts"] <= pd.Timestamp(as_of)]
    if rows.empty:
        return None

    if c["market_class"] == "WINNER":
        sel = _draw_rows(rows) if is_draw_contract(c) else _team_rows(rows, c.get("long_team_name"))
    elif c["market_class"] == "TOTAL":
        sel = rows[(rows["outcome"].map(norm) == "over") & rows["point"].map(lambda p: _same_point(p, c.get("line")))]
    else:  # SPREAD
        sgn = spread_sign(c.get("market_slug"))
        if sgn == 0 or c.get("line") is None:
            return None
        signed = sgn * float(c["line"])
        sel = _team_rows(rows, c.get("long_team_name"))
        sel = sel[sel["point"].map(lambda p: _same_point(p, signed))]
    if sel.empty:
        return None

    sel = sel.sort_values("ts")
    last = sel.iloc[-1]
    age = (pd.Timestamp(as_of) - last["ts"]).total_seconds() / 60.0
    if age > max_age_minutes:
        return None
    earlier = sel[sel["ts"] <= last["ts"] - pd.Timedelta(minutes=15)]
    fair_15 = float(earlier.iloc[-1]["fair_prob"]) if not earlier.empty else None
    return {
        "pin_event_id": pin_event_id,
        "pin_market": market_key,
        "pin_ts": last["ts"],
        "pin_age_min": round(age, 1),
        "pin_price": float(last["price"]),
        "fair": float(last["fair_prob"]),
        "fair_15m_ago": fair_15,
        "pin_move_15m": (float(last["fair_prob"]) - fair_15) if fair_15 is not None else None,
        "match_how": mt.iloc[0]["how"],
        "n_pin_snapshots": int(len(sel)),
    }


def last_fair_before(fair: pd.DataFrame, pin_event_id, market_key: str, selector, before: datetime) -> dict | None:
    """Latest Pinnacle fair for a selected outcome strictly before `before` (grading)."""
    rows = fair[(fair["event_id"] == pin_event_id) & (fair["market"] == market_key)]
    rows = rows[rows["ts"] < pd.Timestamp(before)]
    rows = selector(rows)
    if rows.empty:
        return None
    last = rows.sort_values("ts").iloc[-1]
    return {"pin_ts": last["ts"], "fair": float(last["fair_prob"]), "pin_price": float(last["price"])}
