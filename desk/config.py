"""Load config/desk.yaml and resolve the sports-method code path.

sports-method is imported at run time (its devig, fees, metrics, matcher and
loaders are the single source of truth for that arithmetic). The GitHub
Actions workflow clones it at the pinned SHA into ./vendor/sports-method; a
local run can point SPORTS_METHOD_PATH at any checkout.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "desk.yaml"


def load_config(path: Path | str = CONFIG) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def ensure_sports_method(cfg: dict | None = None) -> Path:
    """Put the sports-method checkout on sys.path and return its path.

    Order: $SPORTS_METHOD_PATH, ./vendor/sports-method, ../devrongray/sports-method.
    """
    cands = []
    if os.environ.get("SPORTS_METHOD_PATH"):
        cands.append(Path(os.environ["SPORTS_METHOD_PATH"]))
    cands.append(ROOT / "vendor" / "sports-method")
    cands.append(ROOT.parent / "devrongray" / "sports-method")
    for c in cands:
        if (c / "method" / "devig.py").exists():
            if str(c) not in sys.path:
                sys.path.insert(0, str(c))
            return c
    raise RuntimeError(
        "sports-method not found. Set SPORTS_METHOD_PATH to a checkout of "
        "https://github.com/Devrongray/sports-method (the workflow clones it into vendor/)."
    )
