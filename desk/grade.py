"""Grade orders, fills and candidates against the Pinnacle close.

Primary benchmark: Pinnacle's last de-vigged price before start (fair_close),
from sports-method's recordings or the desk's period poll. Secondary: Polymarket
US's own last pre-game mid (thin, display rule undocumented; reported, not used
for decisions). Outcome: Polymarket US settlement (1 or 0 for Yes).

    clv_pts (long)  = fair_close − fill_price − fee_per_contract
    clv_pts (short) = fill_price − fair_close − fee_per_contract
    pnl_usd (long)  = contracts × (settlement − fill_price) − fee
    pnl_usd (short) = contracts × (fill_price − settlement) − fee

Unfilled posts get a "would-have" CLV at their post price; every candidate
gets one at its post price (live actions) or its mid (watch rows), so the
scanner is graded on everything it surfaced, not only what was taken.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import data as D
from .config import ensure_sports_method
from .ledger import CAND_COLS, FILL_COLS, ORDER_COLS, read_csv
from .reference import contract_reference, fair_table, match_table

ensure_sports_method()
from method.fees import taker_fee  # noqa: E402
from method.metrics import calibration_fit  # noqa: E402

GRADE_COLS = ["kind", "id", "market_slug", "sport", "market_class", "segment", "quote_state", "action", "side",
              "price", "contracts", "start", "fair_at_entry", "fair_close", "pin_close_ts", "pm_last_mid",
              "settlement", "clv_pts", "fee_per_contract", "pnl_usd", "graded_ts", "note"]


def _f(x):
    try:
        v = float(x)
        return None if math.isnan(v) else v
    except (TypeError, ValueError):
        return None


def _close_reference(c: dict, cfg: dict, data_dir: Path, desk_root: Path, cache: dict) -> dict | None:
    """Pinnacle fair strictly before start for one contract, via the same matcher the scan uses."""
    start = pd.Timestamp(c["start"])
    if pd.isna(start):
        return None
    key = start.floor("h")
    if key not in cache:
        as_of = start.to_pydatetime() - timedelta(seconds=1)
        markets = D.latest_markets(data_dir, as_of, desk_root)
        pin = D.all_pinnacle_rows(data_dir, desk_root, as_of, hours=12)
        fair = fair_table(pin, cfg["reference"]["devig_method"])
        matches = match_table(markets, pin, cfg["reference"]["match_tolerance_minutes"]) if not markets.empty else pd.DataFrame()
        mrows = {r["market_slug"]: r for r in markets.to_dict("records")} if not markets.empty else {}
        cache[key] = (fair, matches, mrows)
    fair, matches, mrows = cache[key]
    row = mrows.get(c["market_slug"])
    if row is None or fair.empty or matches.empty:
        return None
    as_of = start.to_pydatetime() - timedelta(seconds=1)
    return contract_reference(row, fair, matches, cfg["segments"], as_of, max_age_minutes=240)


def grade_all(cfg: dict, data_dir: Path, desk_root: Path, now: datetime | None = None) -> pd.DataFrame:
    now = now or D.utcnow()
    orders = read_csv(desk_root / "ledger" / "orders.csv", ORDER_COLS)
    fills = read_csv(desk_root / "ledger" / "fills.csv", FILL_COLS)
    cands = read_csv(desk_root / "ledger" / "candidates.csv", CAND_COLS)
    hist = D.load_histories(data_dir)
    cache: dict = {}
    out: list[dict] = []

    def settle_info(slug):
        doc = hist.get(slug) or {}
        lp = doc.get("last_pregame") or {}
        return _f(lp.get("mid")), _f(doc.get("settlement"))

    # fills (and taker orders, which are filled at entry)
    fills_by_order = fills.groupby("order_id") if not fills.empty else None
    for o in orders.to_dict("records"):
        if not o.get("start") or pd.Timestamp(o["start"]) > pd.Timestamp(now):
            continue
        ref = _close_reference(o, cfg, data_dir, desk_root, cache)
        fair_close = ref["fair"] if ref else None
        pm_mid, settlement = settle_info(o["market_slug"])
        side = o["side"]
        ofills = fills_by_order.get_group(o["order_id"]) if (fills_by_order is not None and o["order_id"] in fills_by_order.groups) else pd.DataFrame()
        if not ofills.empty:
            for fl in ofills.to_dict("records"):
                px, n = _f(fl["price"]), _f(fl["contracts"]) or 0.0
                fee_total = _f(fl["fee_usd"])
                if fee_total is None:
                    fee_total = (taker_fee(px, cfg["rules"]["fee_coefficient"]) * n) if o["order_type"] == "take" and px else 0.0
                fee_pc = (fee_total / n) if n else 0.0
                clv = None if (fair_close is None or px is None) else ((fair_close - px) if side == "long" else (px - fair_close)) - fee_pc
                pnl = None if (settlement is None or px is None) else (n * ((settlement - px) if side == "long" else (px - settlement)) - fee_total)
                out.append({"kind": "fill", "id": fl["fill_id"], "market_slug": o["market_slug"], "sport": o["sport"],
                            "market_class": o["market_class"], "segment": o["segment"], "quote_state": "", "action": o["order_type"],
                            "side": side, "price": px, "contracts": n, "start": o["start"], "fair_at_entry": o.get("fair_at_entry"),
                            "fair_close": fair_close, "pin_close_ts": ref["pin_ts"] if ref else None, "pm_last_mid": pm_mid,
                            "settlement": settlement, "clv_pts": None if clv is None else round(clv, 4), "fee_per_contract": round(fee_pc, 5),
                            "pnl_usd": None if pnl is None else round(pnl, 2), "graded_ts": now.isoformat(timespec="seconds"), "note": ""})
        else:
            px = _f(o["price"])
            clv = None if (fair_close is None or px is None) else ((fair_close - px) if side == "long" else (px - fair_close))
            out.append({"kind": "post_unfilled", "id": o["order_id"], "market_slug": o["market_slug"], "sport": o["sport"],
                        "market_class": o["market_class"], "segment": o["segment"], "quote_state": "", "action": o["order_type"],
                        "side": side, "price": px, "contracts": _f(o["contracts"]), "start": o["start"], "fair_at_entry": o.get("fair_at_entry"),
                        "fair_close": fair_close, "pin_close_ts": ref["pin_ts"] if ref else None, "pm_last_mid": pm_mid,
                        "settlement": settlement, "clv_pts": None if clv is None else round(clv, 4), "fee_per_contract": 0.0,
                        "pnl_usd": None, "graded_ts": now.isoformat(timespec="seconds"), "note": f"status {o['status']}"})

    # candidates: one grade per (market_slug, action) at the last scan before start
    if not cands.empty:
        cd = cands[cands["start"] != ""].copy()
        cd = cd[pd.to_datetime(cd["start"], utc=True, errors="coerce") <= pd.Timestamp(now)]
        cd = cd.sort_values("scan_ts").groupby(["market_slug", "action"], as_index=False).last()
        for c in cd.to_dict("records"):
            ref = _close_reference(c, cfg, data_dir, desk_root, cache)
            fair_close = ref["fair"] if ref else None
            pm_mid, settlement = settle_info(c["market_slug"])
            live = c["action"] in ("post_bid", "post_ask", "take_long", "take_short")
            px = _f(c["post_px"]) if live else _f(c["mid"])
            side = c["side"] if live else "long"
            clv = None if (fair_close is None or px is None) else ((fair_close - px) if side == "long" else (px - fair_close))
            out.append({"kind": "candidate", "id": f"{c['scan_ts']}|{c['market_slug']}", "market_slug": c["market_slug"],
                        "sport": c["sport"], "market_class": c["market_class"], "segment": c["segment"], "quote_state": c["quote_state"],
                        "action": c["action"], "side": side, "price": px, "contracts": None, "start": c["start"],
                        "fair_at_entry": c["fair"], "fair_close": fair_close, "pin_close_ts": ref["pin_ts"] if ref else None,
                        "pm_last_mid": pm_mid, "settlement": settlement, "clv_pts": None if clv is None else round(clv, 4),
                        "fee_per_contract": 0.0, "pnl_usd": None, "graded_ts": now.isoformat(timespec="seconds"), "note": ""})
    df = pd.DataFrame(out, columns=GRADE_COLS)
    (desk_root / "ledger").mkdir(parents=True, exist_ok=True)
    df.to_csv(desk_root / "ledger" / "grades.csv", index=False)
    return df


def _stats(x: pd.Series) -> dict:
    v = pd.to_numeric(x, errors="coerce").dropna()
    n = int(len(v))
    if n == 0:
        return {"n": 0, "mean": None, "se": None, "t": None}
    mean = float(v.mean())
    se = float(v.std(ddof=1) / math.sqrt(n)) if n > 1 else None
    t = (mean / se) if se else None
    return {"n": n, "mean": round(mean, 4), "se": None if se is None else round(se, 4), "t": None if t is None else round(t, 2)}


def summary_markdown(grades: pd.DataFrame, cfg: dict, now: datetime | None = None) -> str:
    now = now or D.utcnow()
    lines = [f"# Desk scorecard {now.isoformat(timespec='seconds')}", ""]
    if grades.empty:
        lines.append("Nothing graded yet: no orders or candidates whose games have started.")
        return "\n".join(lines) + "\n"
    fills = grades[grades["kind"] == "fill"]
    posts = grades[grades["kind"] == "post_unfilled"]
    cands = grades[grades["kind"] == "candidate"]
    live_c = cands[cands["action"].isin(["post_bid", "post_ask", "take_long", "take_short"])]

    def fmt(v, spec):
        return "" if v is None else format(v, spec)

    def row(label, s, extra=""):
        return f"| {label} | {s['n']} | {fmt(s['mean'], '+.4f')} | {fmt(s['se'], '.4f')} | {fmt(s['t'], '.2f')} | {extra} |"

    lines += ["Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. "
              "Decisions use the t statistic on fills once n is in the hundreds; everything else is context.", "",
              "| set | n | mean CLV | se | t | note |", "|---|---|---|---|---|---|"]
    fs = _stats(fills["clv_pts"])
    pnl = pd.to_numeric(fills["pnl_usd"], errors="coerce").dropna()
    lines.append(row("fills (what you actually hold)", fs, f"P&L ${pnl.sum():+,.2f} on {len(pnl)} settled" if len(pnl) else ""))
    lines.append(row("unfilled posts (would-have, at post price)", _stats(posts["clv_pts"])))
    lines.append(row("live-action candidates (scanner, at post price)", _stats(live_c["clv_pts"])))
    lines.append(row("all referenced candidates (at mid)", _stats(cands["clv_pts"])))
    n_posts = int(len(posts)) + int(len(fills[fills["action"] == "post"]))
    if n_posts:
        lines.append("")
        lines.append(f"Fill rate on posted orders: {len(fills[fills['action'] == 'post'])}/{n_posts} = {len(fills[fills['action'] == 'post']) / n_posts:.0%}.")
    for col, title in (("sport", "By sport"), ("quote_state", "By quote state"), ("segment", "By segment")):
        g = live_c.groupby(col)["clv_pts"] if not live_c.empty else None
        if g is None or len(g) == 0:
            continue
        lines += ["", f"## {title} (live-action candidates)", "", "| group | n | mean CLV | se | t |", "|---|---|---|---|---|"]
        for k, s in g:
            st = _stats(s)
            if st["n"]:
                lines.append(f"| {k or '—'} | {st['n']} | {fmt(st['mean'], '+.4f')} | {fmt(st['se'], '.4f')} | {fmt(st['t'], '.2f')} |")
    # Pinnacle fair calibration on Polymarket settlements (test of the reference itself)
    cal = cands.dropna(subset=["fair_close", "settlement"])
    cal = cal[pd.to_numeric(cal["settlement"], errors="coerce").isin([0.0, 1.0])]
    lines += ["", "## Is Pinnacle's close calibrated on Polymarket US settlements?", ""]
    if len(cal) >= 30:
        fit = calibration_fit(pd.to_numeric(cal["fair_close"]), pd.to_numeric(cal["settlement"]))
        lines.append(f"n = {fit.n}; slope {fit.slope:.3f} (95% CI {fit.slope_ci95[0]:.2f}–{fit.slope_ci95[1]:.2f}); intercept {fit.intercept:+.3f}. "
                     "Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.")
    else:
        lines.append(f"{len(cal)} settled, referenced contracts so far; the fit is reported from 30, read from 200+.")
    lines += ["", "Kill rules and thresholds: PREREGISTRATION.md."]
    return "\n".join(lines) + "\n"
