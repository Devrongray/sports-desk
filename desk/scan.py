"""The scan: every upcoming Polymarket US main-line contract, its quote state,
its Pinnacle reference, and the one action the pre-registered rules allow.

Actions
    post_bid    rest a bid for Yes at fair − margin (or one tick above the best bid, if higher)
    post_ask    rest an ask for Yes at fair + margin (or one tick below the best ask, if lower);
                selling Yes is buying No
    take_long   buy Yes at the ask: only when fair − ask − fee clears the taker rule (rare)
    take_short  sell Yes at the bid (buy No): the mirror of take_long
    watch       referenced but outside the posting window, or no reference yet
    pass        inside the window but nothing qualifies, or Pinnacle just moved

Edges are in probability points (dollars per $1 contract). A maker pays no fee
(retail tier from 19 Oct 2026); a taker pays coefficient × p × (1 − p).
"""
from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

import pandas as pd

from .config import ensure_sports_method, load_config
from . import data as D
from .reference import contract_reference, fair_table, match_table

ensure_sports_method()
from method.fees import taker_fee  # noqa: E402

ACTIONS_LIVE = ("post_bid", "post_ask", "take_long", "take_short")


# --- small helpers ------------------------------------------------------------

def floor_tick(x: float, tick: float) -> float:
    return math.floor(x / tick + 1e-9) * tick


def ceil_tick(x: float, tick: float) -> float:
    return math.ceil(x / tick - 1e-9) * tick


def quote_state(bid: float | None, ask: float | None, rules: dict) -> str:
    if bid is None or ask is None or not (0 < bid < 1 and 0 < ask < 1) or ask <= bid:
        return "none"
    sp = ask - bid
    if sp <= rules["tight_spread_max"] + 1e-9:
        return "tight"
    if sp >= rules["unquoted_spread_min"] - 1e-9:
        return "unquoted"
    return "wide"


def _f(x) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(v) else v


def contract_quote(c: dict, q: dict | None) -> dict:
    """Best bid/ask/depth for a contract: the BBO row when we have one, else the
    market row's quotes, else the two side prices."""
    bid = ask = None
    bid_sh = ask_sh = None
    src = "none"
    q_ts = None
    if q is not None:
        bid, ask = _f(q.get("best_bid")), _f(q.get("best_ask"))
        bid_sh, ask_sh = _f(q.get("bid_shares")), _f(q.get("ask_shares"))
        q_ts = q.get("ts")
        src = "bbo"
    if bid is None or ask is None:
        bid, ask = _f(c.get("best_bid_quote")), _f(c.get("best_ask_quote"))
        src = "market" if bid is not None else src
        q_ts = c.get("ts")
    if bid is None or ask is None:
        ps = [p for p in (_f(s.get("price")) for s in (c.get("sides") or [])) if p is not None]
        if len(ps) >= 2:
            bid, ask = min(ps), max(ps)
            src = "sides"
    return {"bid": bid, "ask": ask, "bid_shares": bid_sh, "ask_shares": ask_sh, "quote_src": src, "quote_ts": q_ts}


def evaluate(c: dict, quote: dict, ref: dict | None, rules: dict, desk: dict, as_of: datetime) -> dict:
    """One contract -> one row with quote state, edges, action, size and reason."""
    start = c.get("start")
    mts = (pd.Timestamp(start) - pd.Timestamp(as_of)).total_seconds() / 60.0 if pd.notna(start) else float("nan")
    tick = _f(c.get("tick")) or 0.01
    coef = _f(c.get("fee_coefficient")) or rules["fee_coefficient"]
    bid, ask = quote["bid"], quote["ask"]
    state = quote_state(bid, ask, rules)
    spread = (ask - bid) if state != "none" else None
    mid = (bid + ask) / 2 if state != "none" else None
    bid_usd = (quote["bid_shares"] * bid) if (quote["bid_shares"] is not None and bid) else None
    ask_usd = (quote["ask_shares"] * ask) if (quote["ask_shares"] is not None and ask) else None

    row = {
        "sport": c["sport"], "market_class": c["market_class"], "segment": c["segment"], "line": c.get("line"),
        "event_title": c.get("event_title"), "question": c.get("question"), "market_slug": c.get("market_slug"),
        "long_team": c.get("long_team_name"), "start": start, "minutes_to_start": round(mts, 1) if mts == mts else None,
        "bid": bid, "ask": ask, "spread": spread, "mid": mid, "quote_state": state,
        "bid_usd": bid_usd, "ask_usd": ask_usd, "tick": tick, "fee_coef": coef,
        "quote_src": quote["quote_src"], "quote_ts": quote["quote_ts"],
        "fair": None, "pin_market": None, "pin_ts": None, "pin_age_min": None, "pin_move_15m": None,
        "mid_minus_fair": None, "taker_long_net": None, "taker_short_net": None,
        "maker_bid_px": None, "maker_bid_edge": None, "maker_ask_px": None, "maker_ask_edge": None,
        "action": "watch", "side": None, "post_px": None, "edge_pts": None,
        "size_usd": None, "contracts": None, "reason": None, "flags": "",
    }
    in_window = (mts == mts) and rules["post_window_minutes"][0] <= mts <= rules["post_window_minutes"][1]

    if ref is None:
        row["reason"] = "no Pinnacle reference" if state != "none" else "no quote, no reference"
        return row
    fair = ref["fair"]
    row.update({"fair": round(fair, 4), "pin_market": ref["pin_market"], "pin_ts": ref["pin_ts"],
                "pin_age_min": ref["pin_age_min"], "pin_move_15m": ref["pin_move_15m"]})
    if state == "none":
        row["reason"] = "referenced, no usable quote"
        return row
    row["mid_minus_fair"] = round(mid - fair, 4)

    # Taker edges after fee (fee is symmetric in p and 1-p)
    fee_ask, fee_bid = taker_fee(ask, coef), taker_fee(bid, coef)
    t_long = fair - ask - fee_ask
    t_short = bid - fair - fee_bid
    row["taker_long_net"], row["taker_short_net"] = round(t_long, 4), round(t_short, 4)

    # Maker prices: at fair ∓ margin, but never worse than one tick inside the current book
    m = rules["margin_pts"]
    mb = min(floor_tick(fair - m, tick), floor_tick(ask - tick, tick))
    ma = max(ceil_tick(fair + m, tick), ceil_tick(bid + tick, tick))
    mb_ok = mb >= bid + tick - 1e-9 and 0 < mb < 1
    ma_ok = ma <= ask - tick + 1e-9 and 0 < ma < 1
    if mb_ok:
        row["maker_bid_px"], row["maker_bid_edge"] = round(mb, 4), round(fair - mb, 4)
    if ma_ok:
        row["maker_ask_px"], row["maker_ask_edge"] = round(ma, 4), round(ma - fair, 4)

    flags = []
    # Decision
    if ref["pin_move_15m"] is not None and abs(ref["pin_move_15m"]) > rules["pinnacle_recent_move_pts"]:
        row["action"], row["reason"] = ("pass" if in_window else "watch"), f"Pinnacle moved {ref['pin_move_15m']:+.3f} in 15 min; you are late"
        return row
    cands = []
    if mb_ok and (fair - mb) >= rules["min_maker_edge_pts"] and mb >= rules["never_buy_below"]:
        cands.append(("post_bid", "long", mb, fair - mb))
    if ma_ok and (ma - fair) >= rules["min_maker_edge_pts"] and (1 - ma) >= rules["never_buy_below"]:
        cands.append(("post_ask", "short", ma, ma - fair))
    half = 0.5 * spread
    if not cands:
        if t_long >= rules["taker_min_edge_pts"] + half and ask >= rules["never_buy_below"] and (ask_usd or 0) >= desk["taker_depth_min_usd"]:
            cands.append(("take_long", "long", ask, t_long))
        if t_short >= rules["taker_min_edge_pts"] + half and (1 - bid) >= rules["never_buy_below"] and (bid_usd or 0) >= desk["taker_depth_min_usd"]:
            cands.append(("take_short", "short", bid, t_short))
    if not cands:
        row["action"] = "pass" if in_window else "watch"
        why = {"tight": "machine-quoted within the margin of Pinnacle", "wide": "wide quote but the book is already inside fair ∓ margin",
               "unquoted": "unquoted and fair is outside the postable range"}[state]
        row["reason"] = why if in_window else f"outside posting window ({why})"
        return row
    action, side, px, edge = max(cands, key=lambda t: t[3])
    unit = desk["unit_usd"]
    cost_per_contract = px if side == "long" else (1 - px)
    contracts = unit / cost_per_contract
    if action.startswith("take"):
        depth_usd = ask_usd if side == "long" else bid_usd
        cap = desk["taker_depth_fraction"] * (depth_usd or 0)
        if cap < unit:
            contracts = cap / cost_per_contract
            flags.append(f"size capped by depth ${depth_usd:,.0f}")
    buy_px = px if side == "long" else 1 - px
    if buy_px < rules["avoid_buy_below"]:
        flags.append(f"buying under {rules['avoid_buy_below']:.2f}")
    if state == "unquoted":
        flags.append("unquoted book: fills come only from retail crossing")
    row.update({"side": side, "post_px": round(px, 4), "edge_pts": round(edge, 4),
                "size_usd": round(contracts * cost_per_contract, 2), "contracts": round(contracts, 2)})
    if in_window:
        row["action"] = action
        row["reason"] = {"post_bid": f"{state} quote; bid {px:.3f} vs fair {fair:.3f}",
                         "post_ask": f"{state} quote; ask {px:.3f} vs fair {fair:.3f} (sell Yes = buy No)",
                         "take_long": f"ask {ask:.3f} clears fair {fair:.3f} after fee",
                         "take_short": f"bid {bid:.3f} clears fair {fair:.3f} after fee"}[action]
    else:
        row["action"] = "watch"
        row["reason"] = f"would {action} at {px:.3f} (edge {edge:+.3f}); outside posting window"
    row["flags"] = "; ".join(flags)
    return row


# --- the scan -------------------------------------------------------------------

def run_scan(cfg: dict, data_dir: Path, desk_root: Path, as_of: datetime | None = None,
             live: bool = False) -> tuple[pd.DataFrame, dict]:
    """live=True fetches Polymarket US markets and quotes now (needs network: GitHub Actions);
    live=False, or a failed live fetch, uses the recorded files at or before as_of (replay)."""
    as_of = as_of or D.utcnow()
    rules, desk, uni = cfg["rules"], cfg["desk"], cfg["universe"]
    segments = cfg["segments"]
    source = "recorded"
    markets = quotes = pd.DataFrame()
    if live:
        try:
            from .live import live_snapshot
            markets, quotes = live_snapshot(cfg, as_of, desk_root)
            source = "live" if not markets.empty else "recorded"
        except Exception as e:  # noqa: BLE001
            print(f"[warn] live snapshot failed, falling back to recorded data: {e}")
    if markets.empty:
        markets = D.latest_markets(data_dir, as_of, desk_root)
        quotes = D.latest_quotes(data_dir, as_of, lookback_minutes=30, desk_root=desk_root)
    pin = D.all_pinnacle_rows(data_dir, desk_root, as_of, hours=cfg["reference"]["history_hours"])
    meta = {"as_of": as_of.isoformat(timespec="seconds"), "source": source, "markets_rows": int(len(markets)),
            "quote_rows": int(len(quotes)), "pinnacle_rows": int(len(pin)),
            "markets_file": markets["snapshot_file"].iloc[0] if not markets.empty else None}
    if markets.empty:
        return pd.DataFrame(), meta
    # universe filter: upcoming, main line, allowed sport/class
    markets = markets[markets["is_main"] == True]  # noqa: E712
    markets = markets[markets.apply(lambda r: r["sport"] in uni and r["market_class"] in uni[r["sport"]], axis=1)]
    markets = markets[pd.notna(markets["start"]) & (markets["start"] > pd.Timestamp(as_of))]
    fair = fair_table(pin, cfg["reference"]["devig_method"])
    matches = match_table(markets, pin, cfg["reference"]["match_tolerance_minutes"])
    meta.update({"contracts_in_universe": int(len(markets)), "events_matched": int(len(matches)),
                 "fair_rows": int(len(fair))})
    qmap = {r["market_slug"]: r for r in quotes.to_dict("records")} if not quotes.empty else {}
    rows = []
    for c in markets.to_dict("records"):
        ref = contract_reference(c, fair, matches, segments, as_of, cfg["reference"]["pinnacle_max_age_minutes"]) if not fair.empty else None
        rows.append(evaluate(c, contract_quote(c, qmap.get(c["market_slug"])), ref, rules, desk, as_of))
    df = pd.DataFrame(rows)
    if df.empty:
        return df, meta
    live = df["action"].isin(ACTIONS_LIVE)
    df["rank_key"] = df.apply(lambda r: (0 if r["action"] in ACTIONS_LIVE else (1 if r["action"] == "watch" and r["fair"] is not None else 2),
                                         -(abs(r["edge_pts"]) if r["edge_pts"] is not None else (abs(r["mid_minus_fair"]) if r["mid_minus_fair"] is not None else 0))), axis=1)
    df = df.sort_values("rank_key").drop(columns="rank_key").reset_index(drop=True)
    meta.update({"live_actions": int(live.sum()), "referenced": int(df["fair"].notna().sum()),
                 "by_state": df["quote_state"].value_counts().to_dict(),
                 "by_action": df["action"].value_counts().to_dict()})
    return df, meta


# --- outputs ----------------------------------------------------------------------

def _fmt(x, nd=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ""
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def to_markdown(df: pd.DataFrame, meta: dict, cfg: dict, top: int = 25) -> str:
    as_of = meta["as_of"]
    lines = [f"# Desk scan {as_of}", ""]
    lines.append(f"Universe: {meta.get('contracts_in_universe', 0)} upcoming main-line contracts; "
                 f"{meta.get('events_matched', 0)} events matched to Pinnacle; {meta.get('referenced', 0)} contracts with a reference; "
                 f"{meta.get('live_actions', 0)} live actions. Quote states: {meta.get('by_state', {})}.")
    lines.append("")
    if df.empty:
        lines.append("No contracts in the universe at this time.")
        return "\n".join(lines) + "\n"
    live = df[df["action"].isin(ACTIONS_LIVE)]
    lines += ["## Actions inside the posting window", ""]
    if live.empty:
        lines.append("None. Every referenced contract inside the window is either machine-quoted within the margin of Pinnacle or Pinnacle just moved.")
    else:
        lines += ["| # | sport | segment | contract | line | mins | bid | ask | state | fair (ref) | action | price | edge | size $ | flags |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for i, r in enumerate(live.head(top).to_dict("records"), 1):
            lines.append(f"| {i} | {r['sport']} | {r['segment']} | {str(r['question'] or r['event_title'])[:60]} | {_fmt(r['line'], 1)} | "
                         f"{_fmt(r['minutes_to_start'], 0)} | {_fmt(r['bid'])} | {_fmt(r['ask'])} | {r['quote_state']} | "
                         f"{_fmt(r['fair'])} ({r['pin_market']}) | **{r['action']}** | {_fmt(r['post_px'])} | {_fmt(r['edge_pts'])} | "
                         f"{_fmt(r['size_usd'], 2)} | {r['flags']} |")
    watch = df[(df["action"] == "watch") & df["fair"].notna()]
    lines += ["", "## Referenced contracts outside the window (largest gaps first)", ""]
    if watch.empty:
        lines.append("None.")
    else:
        lines += ["| sport | segment | contract | line | mins | bid | ask | state | fair | mid − fair | would | at | edge |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in watch.head(top).to_dict("records"):
            would = r["reason"] if r["reason"] and r["reason"].startswith("would") else ""
            lines.append(f"| {r['sport']} | {r['segment']} | {str(r['question'] or r['event_title'])[:60]} | {_fmt(r['line'], 1)} | "
                         f"{_fmt(r['minutes_to_start'], 0)} | {_fmt(r['bid'])} | {_fmt(r['ask'])} | {r['quote_state']} | {_fmt(r['fair'])} | "
                         f"{_fmt(r['mid_minus_fair'])} | {would.split(' at ')[0].replace('would ', '') if would else ''} | {_fmt(r['post_px'])} | {_fmt(r['edge_pts'])} |")
    passed = df[df["action"] == "pass"]
    lines += ["", f"## Passed inside the window: {len(passed)}", ""]
    for r in passed.head(15).to_dict("records"):
        lines.append(f"- {r['sport']} {r['segment']} {str(r['question'] or r['event_title'])[:70]} — {r['reason']}")
    noref = df[df["fair"].isna()]
    by = noref.groupby(["sport", "quote_state"]).size().reset_index(name="n") if not noref.empty else pd.DataFrame()
    lines += ["", f"## No Pinnacle reference yet: {len(noref)} contracts", ""]
    if not by.empty:
        lines += ["| sport | quote state | n |", "|---|---|---|"]
        lines += [f"| {r['sport']} | {r['quote_state']} | {r['n']} |" for r in by.to_dict("records")]
    lines += ["", "Rules: PREREGISTRATION.md. Edges in probability points per $1 contract; maker pays no fee; "
              f"taker fee {cfg['rules']['fee_coefficient']}·p(1−p)."]
    return "\n".join(lines) + "\n"


def write_outputs(df: pd.DataFrame, meta: dict, cfg: dict, out_root: Path) -> dict:
    as_of = datetime.fromisoformat(meta["as_of"])
    day = as_of.strftime("%Y-%m-%d")
    stamp = as_of.strftime("%Y%m%dT%H%M%SZ")
    d = out_root / "scans" / day
    d.mkdir(parents=True, exist_ok=True)
    csv_path = d / f"scan_{stamp}.csv"
    df.to_csv(csv_path, index=False)
    md = to_markdown(df, meta, cfg)
    (d / f"scan_{stamp}.md").write_text(md)
    (out_root / "scans" / "latest.md").write_text(md)
    df.to_csv(out_root / "scans" / "latest.csv", index=False)
    return {"csv": str(csv_path), "md": str(d / f"scan_{stamp}.md"), "latest": str(out_root / "scans" / "latest.md")}
