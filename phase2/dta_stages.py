"""Disease-stage DTA axis (D4): combine stage-specific and merged-stage sensitivity.

After Derezea, Welton, Rogers & Jones (2026, arXiv:2512.12065): many test-accuracy
studies report sensitivity only for MERGED disease stages (e.g. "stages I-II")
plus the proportion of diseased at each stage, not stage-specific sensitivity.
A merged study's reported sensitivity is the stage-proportion-weighted average of
the latent stage-specific sensitivities:  Se_merged = sum_s p_s * Se_s.

This lets merged studies be INCLUDED alongside stage-specific ones. We estimate
the latent per-stage Se by GLS on the natural scale (where the merged relationship
is linear), and expose the analyst choice {stage-specific only} vs {+ merged} as a
forking-path axis (more studies -> sharper per-stage estimates). Self-audit:
stage-closure (merged obs == p . Se_hat) and stage-monotonicity (later stage at
least as detectable). Boundary: minimal GLS analog of the paper's hierarchical
model; natural-scale (not logit); validated by known-truth recovery + closure.
"""

from __future__ import annotations

import math

import numpy as np


def make_data(se_early: float = 0.60, se_late: float = 0.90,
              n_stage: int = 4, n_merged: int = 4, props=(0.5, 0.5),
              sd: float = 0.04, seed: int = 20260624) -> list[dict]:
    """Stage-specific studies (one per stage) + merged studies reporting the
    proportion-weighted sensitivity. Two stages: 0 = early, 1 = late."""
    rng = np.random.default_rng(seed)
    truth = [se_early, se_late]
    studies: list[dict] = []
    for stage in (0, 1):
        for _ in range(n_stage):
            obs = float(np.clip(rng.normal(truth[stage], sd), 1e-3, 1 - 1e-3))
            studies.append({"type": "stage", "stage": stage, "se_obs": obs, "var": sd ** 2})
    merged_true = props[0] * se_early + props[1] * se_late
    for _ in range(n_merged):
        obs = float(np.clip(rng.normal(merged_true, sd), 1e-3, 1 - 1e-3))
        studies.append({"type": "merged", "props": list(props), "se_obs": obs, "var": sd ** 2})
    return studies


def fit(studies: list[dict], include_merged: bool = True) -> dict:
    """GLS for latent per-stage sensitivity from stage-specific (+ merged) studies."""
    rows, y, w = [], [], []
    for s in studies:
        if s["type"] == "stage":
            a = [0.0, 0.0]; a[s["stage"]] = 1.0
        elif s["type"] == "merged" and include_merged:
            a = list(s["props"])
        else:
            continue
        rows.append(a); y.append(s["se_obs"]); w.append(1.0 / s["var"])
    A = np.asarray(rows, float)
    if np.linalg.matrix_rank(A) < 2:
        raise ValueError("under-identified: need both stages represented")
    W = np.diag(w)
    cov = np.linalg.inv(A.T @ W @ A)
    beta = cov @ A.T @ W @ np.asarray(y, float)
    return {"se_stage": [float(beta[0]), float(beta[1])],
            "se_err": [math.sqrt(max(cov[0, 0], 0.0)), math.sqrt(max(cov[1, 1], 0.0))],
            "n_used": len(rows), "include_merged": include_merged}


def closure_check(studies: list[dict], fitted: dict, tol: float = 0.05) -> dict:
    """Each merged study's observed Se should equal p . Se_hat (within noise)."""
    beta = fitted["se_stage"]
    resids = [s["se_obs"] - (s["props"][0] * beta[0] + s["props"][1] * beta[1])
              for s in studies if s["type"] == "merged"]
    max_abs = max((abs(r) for r in resids), default=0.0)
    return {"max_abs_residual": max_abs, "passes": max_abs <= tol, "n_merged": len(resids)}


def monotonicity_check(fitted: dict) -> dict:
    early, late = fitted["se_stage"]
    return {"monotone": late >= early, "se_early": early, "se_late": late}


def inclusion_axis(studies: list[dict]) -> dict:
    """The D4 forking-path: stage-specific-only vs + merged. Adding merged studies
    should sharpen (not bias) the per-stage estimates."""
    only = fit(studies, include_merged=False)
    both = fit(studies, include_merged=True)
    return {
        "stage_specific_only": {"se_stage": [round(x, 4) for x in only["se_stage"]],
                                "se_err": [round(x, 4) for x in only["se_err"]],
                                "n_used": only["n_used"]},
        "with_merged": {"se_stage": [round(x, 4) for x in both["se_stage"]],
                        "se_err": [round(x, 4) for x in both["se_err"]],
                        "n_used": both["n_used"]},
        "se_narrowed": [both["se_err"][s] <= only["se_err"][s] + 1e-9 for s in (0, 1)],
        "closure": closure_check(studies, both),
        "monotonicity": monotonicity_check(both),
    }


def main() -> int:
    studies = make_data()
    rep = inclusion_axis(studies)
    print("Disease-stage DTA (D4): per-stage sensitivity, stage-specific-only vs +merged\n")
    o, b = rep["stage_specific_only"], rep["with_merged"]
    print(f"  stage-specific only : Se=[{o['se_stage'][0]}, {o['se_stage'][1]}] "
          f"SE=[{o['se_err'][0]}, {o['se_err'][1]}] (n={o['n_used']})")
    print(f"  + merged studies    : Se=[{b['se_stage'][0]}, {b['se_stage'][1]}] "
          f"SE=[{b['se_err'][0]}, {b['se_err'][1]}] (n={b['n_used']})")
    print(f"  SE narrowed by adding merged: {rep['se_narrowed']}")
    print(f"  closure: max|resid|={rep['closure']['max_abs_residual']:.4f} "
          f"passes={rep['closure']['passes']}; monotone={rep['monotonicity']['monotone']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
