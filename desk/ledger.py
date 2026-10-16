"""The desk's own ledger: candidates, orders, fills. Plain CSV, append-only.

    ledger/candidates.csv  every live action and the ten largest referenced gaps per scan
    ledger/orders.csv      what you actually posted or took (you tell the desk; it logs)
    ledger/fills.csv       fills you report (price, contracts, time)
    ledger/grades.csv      written by grade.py

A pass is a row too: candidates that were not posted are graded as "would have"
so the scanner is judged on the whole set, not on the ones you liked.
"""
from __future__ import annotations

import csv
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

from . import data as D
from .scan import ACTIONS_LIVE

CAND_COLS = ["scan_ts", "market_slug", "sport", "market_class", "segment", "line", "question", "long_team", "start",
             "minutes_to_start", "bid", "ask", "spread", "mid", "quote_state", "bid_usd", "ask_usd", "fair", "pin_market",
             "pin_ts", "pin_age_min", "pin_move_15m", "mid_minus_fair", "taker_long_net", "taker_short_net",
             "maker_bid_px", "maker_bid_edge", "maker_ask_px", "maker_ask_edge", "action", "side", "post_px",
             "edge_pts", "size_usd", "contracts", "reason", "flags"]
ORDER_COLS = ["order_id", "logged_ts", "scan_ts", "market_slug", "sport", "market_class", "segment", "line",
              "question", "long_team", "start", "side", "order_type", "price", "contracts", "size_usd",
              "fair_at_entry", "pin_market", "pin_ts_at_entry", "bid_at_entry", "ask_at_entry", "status", "note"]
FILL_COLS = ["fill_id", "order_id", "fill_ts", "price", "contracts", "fee_usd", "note"]


def _append(path: Path, rows: list[dict], cols: list[str]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})
    return len(rows)


def read_csv(path: Path, cols: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


def append_candidates(scan_df: pd.DataFrame, meta: dict, desk_root: Path, top_watch: int = 10) -> int:
    """Live actions plus the ten largest referenced gaps from one scan."""
    if scan_df.empty:
        return 0
    live = scan_df[scan_df["action"].isin(ACTIONS_LIVE)]
    ref = scan_df[(~scan_df["action"].isin(ACTIONS_LIVE)) & scan_df["fair"].notna()].copy()
    ref["abs_gap"] = ref["mid_minus_fair"].abs()
    ref = ref.sort_values("abs_gap", ascending=False).head(top_watch).drop(columns="abs_gap")
    rows = pd.concat([live, ref]).to_dict("records")
    for r in rows:
        r["scan_ts"] = meta["as_of"]
    # one row per (scan_ts, market_slug)
    path = desk_root / "ledger" / "candidates.csv"
    existing = read_csv(path, CAND_COLS)
    have = set(zip(existing["scan_ts"], existing["market_slug"])) if not existing.empty else set()
    rows = [r for r in rows if (r["scan_ts"], r["market_slug"]) not in have]
    return _append(path, rows, CAND_COLS)


def log_order(desk_root: Path, market_slug: str, side: str, order_type: str, price: float, contracts: float,
              note: str = "", when: datetime | None = None) -> dict:
    """Record an order you placed. Entry context (fair, bid/ask, Pinnacle ts) is
    copied from the latest scan row for that contract, so the CLV benchmark is
    pinned to what was known at entry."""
    when = when or D.utcnow()
    latest = desk_root / "scans" / "latest.csv"
    ctx = {}
    if latest.exists():
        s = pd.read_csv(latest, dtype=str, keep_default_na=False)
        hit = s[s["market_slug"] == market_slug]
        if not hit.empty:
            ctx = hit.iloc[0].to_dict()
    row = {
        "order_id": uuid.uuid4().hex[:10], "logged_ts": when.isoformat(timespec="seconds"),
        "scan_ts": ctx.get("scan_ts") or ctx.get("quote_ts") or "", "market_slug": market_slug,
        "sport": ctx.get("sport", ""), "market_class": ctx.get("market_class", ""), "segment": ctx.get("segment", ""),
        "line": ctx.get("line", ""), "question": ctx.get("question", ""), "long_team": ctx.get("long_team", ""),
        "start": ctx.get("start", ""), "side": side, "order_type": order_type, "price": price,
        "contracts": contracts, "size_usd": round(contracts * (price if side == "long" else 1 - price), 2),
        "fair_at_entry": ctx.get("fair", ""), "pin_market": ctx.get("pin_market", ""),
        "pin_ts_at_entry": ctx.get("pin_ts", ""), "bid_at_entry": ctx.get("bid", ""), "ask_at_entry": ctx.get("ask", ""),
        "status": "open" if order_type == "post" else "filled", "note": note,
    }
    _append(desk_root / "ledger" / "orders.csv", [row], ORDER_COLS)
    if order_type == "take":
        log_fill(desk_root, row["order_id"], price, contracts, when=when, fee_usd=None, note="taker fill at entry")
    return row


def log_fill(desk_root: Path, order_id: str, price: float, contracts: float, when: datetime | None = None,
             fee_usd: float | None = None, note: str = "") -> dict:
    when = when or D.utcnow()
    row = {"fill_id": uuid.uuid4().hex[:10], "order_id": order_id, "fill_ts": when.isoformat(timespec="seconds"),
           "price": price, "contracts": contracts, "fee_usd": "" if fee_usd is None else fee_usd, "note": note}
    _append(desk_root / "ledger" / "fills.csv", [row], FILL_COLS)
    _set_status(desk_root, order_id, "filled")
    return row


def cancel_order(desk_root: Path, order_id: str, note: str = "") -> None:
    _set_status(desk_root, order_id, "cancelled", note)


def _set_status(desk_root: Path, order_id: str, status: str, note: str | None = None) -> None:
    path = desk_root / "ledger" / "orders.csv"
    df = read_csv(path, ORDER_COLS)
    if df.empty:
        return
    m = df["order_id"] == order_id
    if not m.any():
        return
    df.loc[m, "status"] = status
    if note:
        df.loc[m, "note"] = (df.loc[m, "note"].astype(str) + " | " + note).str.strip(" |")
    df.to_csv(path, index=False)
