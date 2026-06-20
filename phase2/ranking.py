"""Treatment-hierarchy uncertainty: SUCRA, probability-of-best, and POTH.

POTH (Probability Of the Treatment Hierarchy, Wigle et al. 2025, arXiv:2501.11596)
summarises rank uncertainty into [0,1]. We use the explicit *exact-ordering*
definition: POTH = Monte-Carlo probability that a draw of the relative effects
reproduces the COMPLETE point-estimate hierarchy. POTH < 0.5 => the hierarchy is
non-informative and "X ranks best" must not be asserted (advanced-stats C5).

All MC is seeded for reproducibility (xoshiro-equivalent numpy default_rng).
"""

from __future__ import annotations

import math

import numpy as np


def _sample(effects: dict[str, tuple[float, float]], n: int, seed: int) -> tuple[list[str], np.ndarray]:
    rng = np.random.default_rng(seed)
    names = list(effects)
    cols = []
    for nm in names:
        theta, var = effects[nm]
        sd = math.sqrt(max(var, 0.0))
        cols.append(rng.normal(theta, sd, size=n) if sd > 0 else np.full(n, theta))
    return names, np.column_stack(cols)  # shape (n, T)


def _ranks(draws: np.ndarray, lower_better: bool) -> np.ndarray:
    """Ordinal ranks per draw, rank 1 = best (vectorised). draws shape (n, T).

    Ties are measure-zero for the continuous draws here (placebo is constant but
    cannot tie a continuous active except with probability 0), so ordinal ranks
    match average ranks; this is ~100x faster than apply_along_axis(rankdata).
    """
    x = draws if lower_better else -draws
    order = x.argsort(axis=1, kind="stable")
    n, T = x.shape
    ranks = np.empty((n, T), dtype=float)
    rows = np.arange(n)[:, None]
    ranks[rows, order] = np.arange(1, T + 1, dtype=float)
    return ranks


def sucra(effects, lower_better=True, n=20000, seed=20260620) -> dict[str, float]:
    names, draws = _sample(effects, n, seed)
    ranks = _ranks(draws, lower_better)            # (n, T), 1=best
    T = len(names)
    mean_rank = ranks.mean(axis=0)                  # per treatment
    # SUCRA = (T - mean_rank) / (T - 1), rank 1=best  (Salanti 2011 equivalence)
    return {nm: float((T - mean_rank[i]) / (T - 1)) for i, nm in enumerate(names)}


def prob_best(effects, lower_better=True, n=20000, seed=20260620) -> dict[str, float]:
    names, draws = _sample(effects, n, seed)
    best_idx = (draws.argmin(axis=1) if lower_better else draws.argmax(axis=1))
    counts = np.bincount(best_idx, minlength=len(names))
    return {nm: float(counts[i] / n) for i, nm in enumerate(names)}


def reference_order(effects, lower_better=True) -> tuple[str, ...]:
    items = sorted(effects.items(), key=lambda kv: kv[1][0], reverse=not lower_better)
    return tuple(nm for nm, _ in items)


def poth(effects, lower_better=True, n=20000, seed=20260620) -> float:
    """MC probability of reproducing the complete point-estimate hierarchy."""
    names, draws = _sample(effects, n, seed)
    ref = reference_order(effects, lower_better)
    ref_idx = tuple(names.index(nm) for nm in ref)          # target column order
    order = (draws.argsort(axis=1) if lower_better else (-draws).argsort(axis=1))
    match = np.all(order == np.array(ref_idx), axis=1)
    return float(match.mean())


def hierarchy_report(effects, lower_better=True, n=20000, seed=20260620) -> dict:
    p = poth(effects, lower_better, n, seed)
    return {
        "sucra": sucra(effects, lower_better, n, seed),
        "prob_best": prob_best(effects, lower_better, n, seed),
        "reference_order": list(reference_order(effects, lower_better)),
        "poth": p,
        "informative": p >= 0.5,  # C5 gate
    }
