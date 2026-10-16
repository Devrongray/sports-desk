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
import re
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


def credits_spent_today(desk_root: Path, as_of: datetime) -> float:
    """Sum of credits_spent_est over this UTC day's poll_*.json status files."""
    day_dir = desk_root / "data" / "desk_pinnacle" / as_of.strftime("%Y-%m-%d")
    total = 0.0
    for p in sorted(day_dir.glob("poll_*.json")) if day_dir.exists() else []:
        try:
            total += float(json.loads(p.read_text()).get("credits_spent_est") or 0)
        except (ValueError, OSError):
            continue
    return total


def run_poll(cfg: dict, data_dir: Path, desk_root: Path, as_of: datetime | None = None,
             quota_reserve: float | None = None, max_credits: float | None = None) -> dict:
    as_of = as_of or D.utcnow()
    pm = cfg["period_markets"]
    quota_reserve = pm.get("quota_reserve", 2000) if quota_reserve is None else quota_reserve
    max_credits = pm.get("max_credits_per_run", 60) if max_credits is None else max_credits
    daily_cap = pm.get("daily_credit_cap")
    out = {"ts": as_of.isoformat(timespec="seconds"), "enabled": pm.get("enabled", False), "events": 0, "rows": 0,
           "credits_spent_est": 0, "skipped": None, "quota": None}
    out["key_present"] = bool(os.environ.get("ODDS_API_KEY"))
    if not pm.get("enabled"):
        out["skipped"] = "disabled in config"
        return _finish(out, desk_root, as_of)
    if not out["key_present"]:
        out["skipped"] = "ODDS_API_KEY not set"
        return _finish(out, desk_root, as_of)
    spent_today = credits_spent_today(desk_root, as_of)
    out["credits_spent_today_before"] = spent_today
    if daily_cap is not None and spent_today >= daily_cap:
        out["skipped"] = f"daily credit cap {daily_cap} reached ({spent_today:g} spent today)"
        return _finish(out, desk_root, as_of)
    if daily_cap is not None:
        max_credits = min(max_credits, daily_cap - spent_today)
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


_KEY = re.compile(r"(apiKey=)[^&\s\"']+", re.IGNORECASE)


def _redact(text):
    return _KEY.sub(r"\1***", str(text)) if text is not None else None


def _finish(out: dict, desk_root: Path, as_of: datetime) -> dict:
    """Write the poll status next to the data (also on a skip) and print it.
    Error text is redacted so a key can never land in a committed file."""
    out["skipped"] = _redact(out.get("skipped"))
    day = as_of.strftime("%Y-%m-%d")
    stamp = as_of.strftime("%Y%m%dT%H%M%SZ")
    meta_path = desk_root / "data" / "desk_pinnacle" / day / f"poll_{stamp}.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(out, default=str) + "\n")
    (desk_root / "data" / "desk_pinnacle" / "latest_poll.json").write_text(json.dumps(out, default=str) + "\n")
    print(json.dumps(out, default=str))
    return out
