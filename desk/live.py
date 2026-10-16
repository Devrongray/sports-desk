"""Live Polymarket US snapshot for the scan (run from GitHub Actions, where the gateway is reachable).

Why this exists: on 15 Oct 2026 at about 20:00 UTC the league events endpoint
(/v2/leagues/{slug}/events) started returning only the full-game winner in each
event's nested `markets`, while reporting `marketCounts.numMarkets` of 150–190.
The full list is still served by GET /v1/events/slug/{event_slug}. The desk
fetches that for every upcoming event in its universe, so period, half,
quarter and inning lines are quoted even when the recorder's files are not.

Output frames match desk.data.latest_markets / latest_quotes, and the rows are
also written under data/desk_polymarket/<day>/ so the desk's own history is
complete for grading and replay.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from . import data as D
from .config import ensure_sports_method

ensure_sports_method()
from method import polymarket_us as pm  # noqa: E402


def fetch_event_full(client: "pm.PolymarketUS", event_slug: str) -> dict | None:
    data = client._get(f"/v1/events/slug/{event_slug}", {"groups": "false"})
    if not data:
        return None
    return data.get("event") or data


def live_snapshot(cfg: dict, as_of: datetime, desk_root: Path | None = None, horizon_hours: float = 36,
                  bbo_window_minutes: float | None = None, league_slugs: dict[str, str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Main-line market rows (all segments) and BBO rows for the desk universe, live."""
    uni = cfg["universe"]
    rules = cfg["rules"]
    slugs = league_slugs or {"nhl": "nhl", "nba": "nba", "mlb": "mlb", "ncaab": "cbb", "nfl": "nfl", "cs2": "cs2", "lol": "lol"}
    bbo_window = bbo_window_minutes if bbo_window_minutes is not None else rules["post_window_minutes"][1]
    client = pm.PolymarketUS()
    ts = as_of.isoformat(timespec="seconds")
    horizon = timedelta(hours=horizon_hours)
    market_rows: list[dict] = []
    for sport, keep in uni.items():
        league = slugs.get(sport)
        if not league:
            continue
        try:
            events = client.league_events(league)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] live league {league}: {e}")
            continue
        for ev in events:
            start = pm.parse_iso(pm.event_start(ev))
            if start is None or ev.get("ended") or ev.get("closed"):
                continue
            if not (as_of < start <= as_of + horizon):
                continue
            nested = ev.get("markets") or []
            counts = ev.get("marketCounts") or {}
            want_full = int(counts.get("numMarkets") or 0) > len(nested) or len(nested) <= 1
            full = None
            if want_full and ev.get("slug"):
                try:
                    full = fetch_event_full(client, ev["slug"])
                except Exception as e:  # noqa: BLE001
                    print(f"[warn] live event {ev.get('slug')}: {e}")
            src = full if (full and (full.get("markets") or [])) else ev
            # keep the league event's own fields when the full doc lacks them
            merged = {**ev, **{k: v for k, v in src.items() if v is not None}}
            mts = (start - as_of).total_seconds() / 60.0
            for row in pm.normalize_event_markets(merged, league, keep_classes=set(keep), main_only=True):
                row["sport"] = sport
                row["role"] = "desk"
                row["minutes_to_start"] = mts
                row["ts"] = ts
                row["snapshot_file"] = "live"
                teams = row.get("teams") or []
                long_side = next((s for s in (row.get("sides") or []) if s.get("long")), None)
                row["team_names"] = [t.get("name") for t in teams]
                row["team_abbrs"] = [t.get("abbr") for t in teams]
                row["long_team_id"] = long_side.get("team_id") if long_side else None
                row["long_team_name"] = next((t.get("name") for t in teams if long_side and t.get("id") == long_side.get("team_id")), None)
                market_rows.append(row)
    markets = pd.DataFrame(market_rows)
    quotes_rows: list[dict] = []
    if not markets.empty:
        markets["ts"] = pd.to_datetime(markets["ts"], utc=True)
        markets["start"] = pd.to_datetime(markets["start"], utc=True, errors="coerce")
        near = markets[(markets["minutes_to_start"] >= 0) & (markets["minutes_to_start"] <= bbo_window)]
        for m in near.to_dict("records"):
            slug = m.get("market_slug")
            if not slug:
                continue
            try:
                md = client.bbo(slug)
            except Exception as e:  # noqa: BLE001
                print(f"[warn] live bbo {slug}: {e}")
                continue
            if md:
                quotes_rows.append({"ts": ts, "sport": m["sport"], "event_id": m["event_id"], "start": m["start"],
                                    "market_type": m["market_type"], "market_class": m["market_class"], "segment": m["segment"],
                                    "line": m["line"], "minutes_to_start": round(m["minutes_to_start"], 2), "pass_scope": "desk",
                                    **pm.normalize_bbo(md)})
    quotes = pd.DataFrame(quotes_rows)
    if not quotes.empty:
        quotes["ts"] = pd.to_datetime(quotes["ts"], utc=True)
    if desk_root is not None:
        day = as_of.strftime("%Y-%m-%d")
        stamp = as_of.strftime("%Y%m%dT%H%M%SZ")
        if not markets.empty:
            D.write_ndjson_gz(desk_root / "data" / "desk_polymarket" / day / f"markets_{stamp}.ndjson.gz",
                              [{k: v for k, v in r.items() if k not in ("snapshot_file",)} for r in markets.assign(
                                  ts=markets["ts"].astype(str), start=markets["start"].astype(str)).to_dict("records")])
        if not quotes.empty:
            D.write_ndjson_gz(desk_root / "data" / "desk_polymarket" / day / f"bbo_{stamp}.ndjson.gz",
                              quotes.assign(ts=quotes["ts"].astype(str), start=quotes["start"].astype(str)).to_dict("records"))
    return markets, quotes
