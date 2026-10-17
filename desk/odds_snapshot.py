"""One-shot Pinnacle snapshot for any Odds API sport keys (used by the Begin runs for
sports the recorder does not poll: college football, UFC, soccer leagues, ...).

    python -m desk.odds_snapshot --sports americanfootball_ncaaf,mma_mixed_martial_arts --markets h2h,totals

Cost: (markets returned) x 1 credit per sport per call with bookmakers=pinnacle.
Writes data/odds_snapshots/<day>/<sport>_<ts>.json (raw) and a flat CSV of
de-vigged (additive) fair probabilities, plus latest.csv. Never stores the key;
error text is redacted like the period poll.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from .config import ROOT, ensure_sports_method

ensure_sports_method()
from method.devig import devig  # noqa: E402
from method.odds_api import OddsAPI, normalize_odds  # noqa: E402

_KEY = re.compile(r"(apiKey=)[^&\s\"']+", re.IGNORECASE)
COLS = ["ts", "sport_key", "event_id", "commence_time", "home", "away", "market", "point", "outcome", "price", "fair_prob"]


def snapshot(sports: list[str], markets: tuple[str, ...], out_root: Path, as_of: datetime | None = None) -> dict:
    as_of = as_of or datetime.now(timezone.utc)
    day = as_of.strftime("%Y-%m-%d")
    stamp = as_of.strftime("%Y%m%dT%H%M%SZ")
    out_dir = out_root / "data" / "odds_snapshots" / day
    out_dir.mkdir(parents=True, exist_ok=True)
    status = {"ts": as_of.isoformat(timespec="seconds"), "sports": {}, "quota": None, "key_present": bool(os.environ.get("ODDS_API_KEY"))}
    if not status["key_present"]:
        status["error"] = "ODDS_API_KEY not set"
        return _finish(status, out_root)
    api = OddsAPI()
    rows_out: list[dict] = []
    for sk in sports:
        try:
            events = api.odds(sk, markets)
        except Exception as e:  # noqa: BLE001
            status["sports"][sk] = {"error": _KEY.sub(r"\1***", str(e))[:300]}
            continue
        (out_dir / f"{sk}_{stamp}.json").write_text(json.dumps(events, default=str))
        norm = list(normalize_odds(events, sk, as_of.isoformat(timespec="seconds")))
        # de-vig per (event, market, point) group
        groups: dict[tuple, list[dict]] = {}
        for r in norm:
            groups.setdefault((r["event_id"], r["market"], r.get("point")), []).append(r)
        n_fair = 0
        for key, g in groups.items():
            prices = [float(x["price"]) for x in g if x.get("price")]
            if len(prices) != len(g) or len(prices) < 2:
                continue
            fair = devig(prices, "additive")
            for r, p in zip(g, fair):
                rows_out.append({**{c: r.get(c) for c in COLS if c != "fair_prob"}, "fair_prob": round(float(p), 4)})
                n_fair += 1
        status["sports"][sk] = {"events": len(events), "rows": len(norm), "fair_rows": n_fair}
        status["quota"] = api.quota
    path = out_dir / f"fair_{stamp}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows_out:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in COLS})
    (out_root / "data" / "odds_snapshots" / "latest.csv").write_text(path.read_text())
    status["fair_csv"] = str(path.relative_to(out_root))
    return _finish(status, out_root)


def _finish(status: dict, out_root: Path) -> dict:
    p = out_root / "data" / "odds_snapshots" / "latest_status.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(status, default=str) + "\n")
    print(json.dumps(status, default=str))
    return status


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="desk.odds_snapshot")
    ap.add_argument("--sports", required=True, help="comma-separated Odds API sport keys")
    ap.add_argument("--markets", default="h2h,totals")
    ap.add_argument("--out", default=str(ROOT))
    a = ap.parse_args(argv)
    snapshot([s.strip() for s in a.sports.split(",") if s.strip()], tuple(m.strip() for m in a.markets.split(",") if m.strip()), Path(a.out))


if __name__ == "__main__":
    main()
