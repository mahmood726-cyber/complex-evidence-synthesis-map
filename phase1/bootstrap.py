"""Locate sibling portfolio repos without hardcoding machine-specific paths.

The Phase-1 work reuses two sibling repositories verbatim (reuse, don't
re-implement):
  - advanced-nma-pooling : the aggregate-data NMA estimator (`nma_pool`)
  - conformal-ma         : the conformal / standard / HKSJ PI primitives

Resolution order for each:
  1. explicit env var (PORTFOLIO_ROOT, or per-repo *_DIR)
  2. sibling of this repo (../<name>)
If a sibling is absent the caller degrades to SKIP-with-reason rather than
failing the whole run (mirrors the R/netmeta SKIP policy).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _portfolio_root() -> Path:
    env = os.environ.get("PORTFOLIO_ROOT")
    if env:
        return Path(env)
    return REPO_ROOT.parent  # sibling layout: C:\Projects\<repo>


def find_repo(name: str, env_var: str | None = None) -> Path | None:
    """Return the path to a sibling repo, or None if it cannot be located."""
    if env_var and os.environ.get(env_var):
        cand = Path(os.environ[env_var])
        return cand if cand.exists() else None
    cand = _portfolio_root() / name
    return cand if cand.exists() else None


def add_advanced_nma_pooling() -> Path | None:
    repo = find_repo("advanced-nma-pooling", "ADVANCED_NMA_POOLING_DIR")
    if repo is None:
        return None
    src = repo / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return repo


def add_conformal_ma() -> Path | None:
    repo = find_repo("conformal-ma", "CONFORMAL_MA_DIR")
    if repo is None:
        return None
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    return repo
