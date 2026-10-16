"""Read sports-method's data branch (and the desk's own period poll) as of a time.

File layout on the data branch (sports-method README):
    data/polymarket/YYYY-MM-DD/markets_<ts>.ndjson.gz   main-line rows, every 10 min
    data/polymarket/YYYY-MM-DD/bbo_<ts>.ndjson.gz       quotes for main lines, full pass
    data/polymarket/YYYY-MM-DD/bbow_<ts>.ndjson.gz      quotes inside the 90-min window, every minute
    data/pinnacle/YYYY-MM-DD/odds_<ts>.ndjson.gz        one row per outcome per pass
    data/polymarket_history/YYYY-MM-DD/<slug>.json.gz   minute path + last_pregame + settlement
Desk's own:
    data/desk_pinnacle/YYYY-MM-DD/period_<ts>.ndjson.gz Pinnacle period/half/quarter lines

<ts> is YYYYMMDDTHHMMSSZ (UTC). `as_of` lets a scan be replayed at any past
moment using only files stamped at or before it.
"""
from __future__ import annotations

import gzip
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

import pandas as pd

_STAMP = re.compile(r"_(\d{8}T\d{6}Z)\.")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_stamp(name: str) -> datetime | None:
    m = _STAMP.search(name)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)


def _ndjson(path: Path) -> Iterator[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _json(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def files_between(root: Path, prefix: str, start: datetime, end: datetime) -> list[Path]:
    """All <prefix>_<stamp>.ndjson.gz under root/<day>/ with start <= stamp <= end, oldest first."""
    if not root.exists():
        return []
    out = []
    for day in sorted(p for p in root.iterdir() if p.is_dir()):
        if day.name < (start - timedelta(days=1)).strftime("%Y-%m-%d") or day.name > end.strftime("%Y-%m-%d"):
            continue
        for f in day.glob(f"{prefix}_*.ndjson.gz"):
            st = parse_stamp(f.name)
            if st is not None and start <= st <= end:
                out.append((st, f))
    return [f for _, f in sorted(out)]


def latest_file(root: Path, prefix: str, as_of: datetime, max_age_hours: float = 24) -> Path | None:
    fs = files_between(root, prefix, as_of - timedelta(hours=max_age_hours), as_of)
    return fs[-1] if fs else None


# --- Polymarket US -----------------------------------------------------------

def _desk_pm_root(desk_root: Path | None) -> Path | None:
    return (desk_root / "data" / "desk_polymarket") if desk_root is not None else None


def _latest_across(roots: list[Path | None], prefix: str, as_of: datetime) -> Path | None:
    """Latest <prefix>_ file across several roots (the recorder's and the desk's own)."""
    best = None
    for root in roots:
        if root is None:
            continue
        f = latest_file(root, prefix, as_of)
        if f is not None:
            st = parse_stamp(f.name)
            if best is None or st > best[0]:
                best = (st, f)
    return best[1] if best else None


def latest_markets(data: Path, as_of: datetime, desk_root: Path | None = None) -> pd.DataFrame:
    """Main-line market rows from the latest markets_ file at or before as_of,
    taken from whichever source (sports-method recorder or the desk's own live
    snapshots) wrote most recently. Keeps teams and sides."""
    f = _latest_across([data / "polymarket", _desk_pm_root(desk_root)], "markets", as_of)
    if f is None:
        return pd.DataFrame()
    rows = []
    for r in _ndjson(f):
        teams = r.get("teams") or []
        long_side = next((s for s in (r.get("sides") or []) if s.get("long")), None)
        r["team_names"] = [t.get("name") for t in teams]
        r["team_abbrs"] = [t.get("abbr") for t in teams]
        r["long_team_id"] = long_side.get("team_id") if long_side else None
        r["long_team_name"] = next((t.get("name") for t in teams if long_side and t.get("id") == long_side.get("team_id")), None)
        r["snapshot_file"] = f.name
        rows.append(r)
    df = pd.DataFrame(rows)
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"], utc=True)
        df["start"] = pd.to_datetime(df["start"], utc=True, errors="coerce")
    return df


def latest_quotes(data: Path, as_of: datetime, lookback_minutes: float = 30, desk_root: Path | None = None) -> pd.DataFrame:
    """Most recent BBO row per market_slug from bbo_/bbow_ files in the lookback
    (recorder and desk sources together)."""
    root = data / "polymarket"
    start = as_of - timedelta(minutes=lookback_minutes)
    fs = files_between(root, "bbo", start, as_of) + files_between(root, "bbow", start, as_of)
    dpr = _desk_pm_root(desk_root)
    if dpr is not None:
        fs += files_between(dpr, "bbo", start, as_of)
    rows = []
    for f in fs:
        scope = "window" if f.name.startswith("bbow_") else "full"
        for r in _ndjson(f):
            r["pass_scope"] = scope
            rows.append(r)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df = df.sort_values("ts").groupby("market_slug", as_index=False).last()
    return df


# --- Pinnacle ---------------------------------------------------------------

def pinnacle_rows(data: Path, as_of: datetime, hours: float = 6) -> pd.DataFrame:
    fs = files_between(data / "pinnacle", "odds", as_of - timedelta(hours=hours), as_of)
    rows = []
    for f in fs:
        rows.extend(_ndjson(f))
    df = pd.DataFrame(rows)
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"], utc=True)
        df["commence_time"] = pd.to_datetime(df["commence_time"], utc=True, errors="coerce")
    return df


def desk_period_rows(desk_root: Path, as_of: datetime, hours: float = 6) -> pd.DataFrame:
    fs = files_between(desk_root / "data" / "desk_pinnacle", "period", as_of - timedelta(hours=hours), as_of)
    rows = []
    for f in fs:
        rows.extend(_ndjson(f))
    df = pd.DataFrame(rows)
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"], utc=True)
        df["commence_time"] = pd.to_datetime(df["commence_time"], utc=True, errors="coerce")
    return df


def all_pinnacle_rows(data: Path, desk_root: Path, as_of: datetime, hours: float = 6) -> pd.DataFrame:
    a = pinnacle_rows(data, as_of, hours)
    b = desk_period_rows(desk_root, as_of, hours)
    if a.empty:
        return b
    if b.empty:
        return a
    return pd.concat([a, b], ignore_index=True)


# --- histories (grading) ------------------------------------------------------

def load_histories(data: Path, since_day: str | None = None) -> dict[str, dict]:
    """market_slug -> history doc (last_pregame, settlement, start, ...)."""
    root = data / "polymarket_history"
    out: dict[str, dict] = {}
    if not root.exists():
        return out
    for day in sorted(p for p in root.iterdir() if p.is_dir()):
        if since_day and day.name < since_day:
            continue
        for f in day.glob("*.json.gz"):
            doc = _json(f)
            slug = doc.get("market_slug") or f.name.replace(".json.gz", "")
            out[slug] = doc
    return out


def write_ndjson_gz(path: Path, rows: list[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":"), default=str) + "\n")
    return len(rows)
