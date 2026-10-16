"""Pinnacle period / half / quarter / inning lines from The Odds API, one event at a time.

The Odds API serves these only through GET /v4/sports/{sport}/events/{eventId}/odds.
Cost per request = (unique markets returned) × (regions); `bookmakers=pinnacle`
counts as one region. Empty responses are free. So the poll runs only for
events inside the posting window and stops when the quota reserve is reached.

Events come from sports-method's Pinnacle rows (same Odds API event ids), so no
extra listing call is needed. Rows are written in the same shape as
sports-method's pinnacle rows, with `sport` set to the desk sport key, so the
same de-vig and matcher work on them.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from . import data as D
from .config import ensure_sports_method

ensure_sports_method()
from method.odds_api import OddsAPI, normalize_odds  # noqa: E402


class OddsAPIEvents(OddsAPI):
    def event_odds(self, sport_key: str, event_id: str, markets: tuple[str, ...], regions: str = "eu",
                   bookmakers: tuple[str, ...] = ("pinnacle",)) -> dict | None:
        data = self._get(f"/sports/{sport_key}/events/{event_id}/odds", {
            "regions": regions, "markets": ",".join(markets), "bookmakers": ",".join(bookmakers),
            "oddsFormat": "decimal", "dateFormat": "iso",
        })
        return data or None


def upcoming_events(data_dir: Path, as_of: datetime, within_minutes: int, sport_keys: dict[str, str]) -> pd.DataFrame:
    """Odds API events (from sports-method's recordings) starting within the window."""
    pin = D.pinnacle_rows(data_dir, as_of, hours=6)
    if pin.empty:
        return pd.DataFrame(columns=["sport", "sport_key", "event_id", "commence_time", "home", "away"])
    ev = pin.sort_values("ts").groupby(["sport", "event_id"], as_index=False).last()[["sport", "sport_key", "event_id", "commence_time", "home", "away"]]
    lo, hi = pd.Timestamp(as_of), pd.Timestamp(as_of) + pd.Timedelta(minutes=within_minutes)
    ev = ev[(ev["commence_time"] > lo) & (ev["commence_time"] <= hi) & ev["sport"].isin(sport_keys)]
    return ev


def run_poll(cfg: dict, data_dir: Path, desk_root: Path, as_of: datetime | None = None,
             quota_reserve: float = 2000, max_credits: float = 60) -> dict:
    as_of = as_of or D.utcnow()
    pm = cfg["period_markets"]
    out = {"ts": as_of.isoformat(timespec="seconds"), "enabled": pm.get("enabled", False), "events": 0, "rows": 0,
           "credits_spent_est": 0, "skipped": None, "quota": None}
    out["key_present"] = bool(os.environ.get("ODDS_API_KEY"))
    if not pm.get("enabled"):
        out["skipped"] = "disabled in config"
        return _finish(out, desk_root, as_of)
    if not out["key_present"]:
        out["skipped"] = "ODDS_API_KEY not set"
        return _finish(out, desk_root, as_of)
    by_sport = pm["by_sport"]
    ev = upcoming_events(data_dir, as_of, pm["within_minutes"], by_sport)
    api = OddsAPIEvents()
    try:
        api.sports()  # free; refreshes quota headers
        out["quota"] = api.quota
    except Exception as e:  # noqa: BLE001
        out["skipped"] = f"odds api unreachable: {e}"
        return _finish(out, desk_root, as_of)
    if ev.empty:
        out["skipped"] = "no events inside the window"
        return _finish(out, desk_root, as_of)
    rows: list[dict] = []
    spent = 0.0
    for e in ev.to_dict("records"):
        markets = tuple(by_sport.get(e["sport"], []))
        if not markets:
            continue
        if api.quota.get("remaining") is not None and api.quota["remaining"] <= quota_reserve:
            out["skipped"] = f"quota reserve reached ({api.quota['remaining']} left)"
            break
        if spent + len(markets) > max_credits:
            out["skipped"] = f"per-run credit cap {max_credits} reached"
            break
        try:
            doc = api.event_odds(e["sport_key"], e["event_id"], markets)
        except Exception as ex:  # noqa: BLE001
            print(f"[warn] event odds {e['sport_key']} {e['event_id']}: {ex}")
            continue
        if not doc:
            continue
        got = {mk.get("key") for bk in doc.get("bookmakers") or [] for mk in bk.get("markets") or []}
        spent += len(got)
        for r in normalize_odds([doc], e["sport_key"], as_of.isoformat(timespec="seconds")):
            r["sport"] = e["sport"]
            rows.append(r)
        out["events"] += 1
    day = as_of.strftime("%Y-%m-%d")
    stamp = as_of.strftime("%Y%m%dT%H%M%SZ")
    if rows:
        out["rows"] = D.write_ndjson_gz(desk_root / "data" / "desk_pinnacle" / day / f"period_{stamp}.ndjson.gz", rows)
    out["credits_spent_est"] = spent
    out["quota"] = api.quota
    return _finish(out, desk_root, as_of)


def _finish(out: dict, desk_root: Path, as_of: datetime) -> dict:
    """Write the poll status next to the data (also on a skip) and print it."""
    day = as_of.strftime("%Y-%m-%d")
    stamp = as_of.strftime("%Y%m%dT%H%M%SZ")
    meta_path = desk_root / "data" / "desk_pinnacle" / day / f"poll_{stamp}.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(out, default=str) + "\n")
    (desk_root / "data" / "desk_pinnacle" / "latest_poll.json").write_text(json.dumps(out, default=str) + "\n")
    print(json.dumps(out, default=str))
    return out
