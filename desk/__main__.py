"""Command line.

    python -m desk scan        --data <sports-method data dir> [--as-of 2026-10-15T22:30:00Z]
    python -m desk poll        --data <sports-method data dir>          # Pinnacle period lines (needs ODDS_API_KEY)
    python -m desk order       --slug <market_slug> --side long|short --type post|take --price 0.57 --contracts 35 [--note ...]
    python -m desk fill        --order <order_id> --price 0.57 --contracts 35 [--fee 0]
    python -m desk cancel      --order <order_id>
    python -m desk grade       --data <sports-method data dir>
    python -m desk replay      --data <dir> --from 2026-10-15T20:00Z --to 2026-10-16T03:00Z --every 30

`--data` is the `data/` directory of a checkout of sports-method's data branch.
Everything the desk writes lands under this repo: scans/, ledger/, data/desk_pinnacle/.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import ROOT, load_config


def _parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def cmd_scan(a):
    from . import ledger
    from .scan import run_scan, write_outputs
    cfg = load_config(a.config)
    as_of = _parse_ts(a.as_of)
    df, meta = run_scan(cfg, Path(a.data), ROOT, as_of, live=a.live)
    paths = write_outputs(df, meta, cfg, ROOT)
    n = ledger.append_candidates(df, meta, ROOT) if not a.no_ledger else 0
    meta["ledger_rows_added"] = n
    meta["paper_positions_added"] = ledger.append_paper(df, meta, ROOT) if not a.no_ledger else 0
    meta["outputs"] = paths
    print(json.dumps(meta, default=str, indent=2))
    if a.print:
        print(Path(paths["latest"]).read_text())


def cmd_poll(a):
    from .period_poll import run_poll
    cfg = load_config(a.config)
    run_poll(cfg, Path(a.data), ROOT, _parse_ts(a.as_of))


def cmd_order(a):
    from . import ledger
    row = ledger.log_order(ROOT, a.slug, a.side, a.type, float(a.price), float(a.contracts), a.note or "")
    print(json.dumps(row, default=str, indent=2))


def cmd_fill(a):
    from . import ledger
    row = ledger.log_fill(ROOT, a.order, float(a.price), float(a.contracts), fee_usd=(float(a.fee) if a.fee is not None else None), note=a.note or "")
    print(json.dumps(row, default=str, indent=2))


def cmd_cancel(a):
    from . import ledger
    ledger.cancel_order(ROOT, a.order, a.note or "")
    print(f"cancelled {a.order}")


def cmd_grade(a):
    from .grade import grade_all, summary_markdown
    cfg = load_config(a.config)
    df = grade_all(cfg, Path(a.data), ROOT)
    md = summary_markdown(df, cfg)
    (ROOT / "ledger").mkdir(exist_ok=True)
    (ROOT / "ledger" / "summary.md").write_text(md)
    print(md)


def cmd_replay(a):
    """Run the scan at several past moments (no ledger writes); prints a compact table."""
    from .scan import run_scan
    cfg = load_config(a.config)
    t, end = _parse_ts(a.frm), _parse_ts(a.to)
    step = timedelta(minutes=a.every)
    print("| as_of | universe | matched | referenced | live | by state | by action |")
    print("|---|---|---|---|---|---|---|")
    while t <= end:
        df, meta = run_scan(cfg, Path(a.data), ROOT, t)
        print(f"| {t.strftime('%m-%d %H:%M')} | {meta.get('contracts_in_universe', 0)} | {meta.get('events_matched', 0)} | "
              f"{meta.get('referenced', 0)} | {meta.get('live_actions', 0)} | {meta.get('by_state', {})} | {meta.get('by_action', {})} |")
        if a.show_live and meta.get("live_actions"):
            live = df[df["action"].isin(["post_bid", "post_ask", "take_long", "take_short"])]
            for r in live.to_dict("records"):
                print(f"    {r['sport']} {r['segment']} {str(r['question'])[:60]} | {r['quote_state']} {r['bid']}/{r['ask']} fair {r['fair']} -> {r['action']} @ {r['post_px']} edge {r['edge_pts']:+.3f}")
        t += step


def main(argv=None):
    p = argparse.ArgumentParser(prog="desk")
    p.add_argument("--config", default=str(ROOT / "config" / "desk.yaml"))
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan"); s.add_argument("--data", required=True); s.add_argument("--as-of", default=None)
    s.add_argument("--live", action="store_true", help="fetch Polymarket US now (GitHub Actions); default reads recorded files")
    s.add_argument("--no-ledger", action="store_true"); s.add_argument("--print", action="store_true"); s.set_defaults(fn=cmd_scan)

    s = sub.add_parser("poll"); s.add_argument("--data", required=True); s.add_argument("--as-of", default=None); s.set_defaults(fn=cmd_poll)

    s = sub.add_parser("order"); s.add_argument("--slug", required=True); s.add_argument("--side", choices=["long", "short"], required=True)
    s.add_argument("--type", choices=["post", "take"], required=True); s.add_argument("--price", required=True)
    s.add_argument("--contracts", required=True); s.add_argument("--note", default=""); s.set_defaults(fn=cmd_order)

    s = sub.add_parser("fill"); s.add_argument("--order", required=True); s.add_argument("--price", required=True)
    s.add_argument("--contracts", required=True); s.add_argument("--fee", default=None); s.add_argument("--note", default=""); s.set_defaults(fn=cmd_fill)

    s = sub.add_parser("cancel"); s.add_argument("--order", required=True); s.add_argument("--note", default=""); s.set_defaults(fn=cmd_cancel)

    s = sub.add_parser("grade"); s.add_argument("--data", required=True); s.set_defaults(fn=cmd_grade)

    s = sub.add_parser("replay"); s.add_argument("--data", required=True); s.add_argument("--from", dest="frm", required=True)
    s.add_argument("--to", required=True); s.add_argument("--every", type=int, default=30); s.add_argument("--show-live", action="store_true")
    s.set_defaults(fn=cmd_replay)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
