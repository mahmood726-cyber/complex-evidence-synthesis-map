"""P0-B (first increment): honest prediction-interval coverage for the NMA effect.

Reuses conformal-ma's audited PI primitives verbatim (conformal / standard /
HKSJ) and adds:
  - `recommend_pi`  : pick the PI method by EMPIRICAL out-of-sample coverage,
                      never defaulting to conformal (encodes conformal-ma's own
                      finding that conformal under-covers at small k).
  - `simulate_coverage` : known-truth Monte-Carlo validation (the R-free path,
                      since netmeta parity is SKIPPED on this box).

This increment operates on the class-pooled active-vs-placebo effect sample
(k=10). Per-contrast PIs (k=2..4 here) are intentionally NOT produced: conformal
requires k>=4 and is only trustworthy at k>=5, so the sparse star network cannot
support honest per-contrast conformal PIs -- a finding, reported, not hidden.
"""

from __future__ import annotations

import math

import numpy as np

from phase1 import bootstrap

bootstrap.add_conformal_ma()
import pipeline as cma  # noqa: E402  (conformal-ma primitives, reused verbatim)

NOMINAL = 0.95


def compute_intervals(yi, sei, alpha: float = 0.05) -> dict:
    """All three PIs on the full sample. Returns theta/tau2 + each interval."""
    yi = np.asarray(yi, dtype=float)
    sei = np.asarray(sei, dtype=float)
    k = len(yi)

    conf = cma.conformal_prediction_set(yi, sei, alpha=alpha)
    if conf is None:
        return {"k": k, "computable": False,
                "reason": f"k={k} < 4: conformal not computable"}

    theta, tau2, se_theta = conf["theta"], conf["tau2"], conf["se_theta"]
    std = cma.standard_prediction_interval(theta, se_theta, tau2, k, alpha)
    hksj = cma.hksj_prediction_interval(yi, sei, theta, tau2, k, alpha)

    return {
        "k": k,
        "computable": True,
        "theta": theta,
        "tau2": tau2,
        "se_theta": se_theta,
        "intervals": {
            "conformal": (conf["conformal_lo"], conf["conformal_hi"]),
            "standard": (std["standard_lo"], std["standard_hi"]) if std else None,
            "hksj": (hksj["hksj_lo"], hksj["hksj_hi"]) if hksj else None,
        },
        "widths": {
            "conformal": conf["conformal_width"],
            "standard": std["standard_width"] if std else math.nan,
            "hksj": hksj["hksj_width"] if hksj else math.nan,
        },
    }


def honest_coverage(yi, sei) -> dict:
    """Leave-one-out empirical coverage per method (reused verbatim)."""
    return cma.heldout_interval_coverage(np.asarray(yi, float), np.asarray(sei, float))


def recommend_pi(coverage: dict, intervals: dict, nominal: float = NOMINAL) -> dict:
    """Recommend the PI method by empirical coverage -- NEVER default to conformal.

    Rule: among methods whose empirical LOO coverage >= nominal, pick the
    narrowest (most efficient). If NONE reach nominal, report meets_nominal=False
    and surface the method closest to nominal from below, flagged as
    under-covering. This is the C1 guardrail in code.
    """
    widths = intervals.get("widths", {})
    qualifying = {
        m: cov for m, cov in coverage.items()
        if cov is not None and not (isinstance(cov, float) and math.isnan(cov)) and cov >= nominal
    }
    if qualifying:
        # narrowest among those that cover at/above nominal
        chosen = min(qualifying, key=lambda m: widths.get(m, math.inf))
        return {"recommended": chosen, "meets_nominal": True,
                "empirical_coverage": coverage[chosen],
                "coverage_table": coverage}
    # none reach nominal -> honest under-coverage report. Among the best-covering
    # methods, pick the NARROWEST (same insufficient coverage, more efficient) --
    # never just the widest by accident.
    valid = {m: c for m, c in coverage.items()
             if c is not None and not (isinstance(c, float) and math.isnan(c))}
    if valid:
        best_cov = max(valid.values())
        tied = [m for m, c in valid.items() if abs(c - best_cov) < 1e-9]
        closest = min(tied, key=lambda m: widths.get(m, math.inf))
    else:
        closest = None
    return {"recommended": closest, "meets_nominal": False,
            "empirical_coverage": valid.get(closest),
            "note": "no PI method reached nominal coverage at this k -- "
                    "intervals under-cover; report as a finding",
            "coverage_table": coverage}


def simulate_coverage(theta_true: float, tau2_true: float, sei_template,
                      n_sims: int = 2000, alpha: float = 0.05,
                      seed: int = 20260620) -> dict:
    """Known-truth PI coverage: does each PI cover a NEW study's true effect?

    For each sim: draw k study true effects ~ N(theta, tau2), observe with the
    template SEs, build PIs, then draw one NEW true effect ~ N(theta, tau2) and
    check containment. Returns empirical coverage + 3-sigma MC half-width.
    """
    rng = np.random.default_rng(seed)
    sei = np.asarray(sei_template, dtype=float)
    k = len(sei)
    hit = {"conformal": 0, "standard": 0, "hksj": 0}
    seen = {"conformal": 0, "standard": 0, "hksj": 0}

    for _ in range(n_sims):
        true_i = rng.normal(theta_true, math.sqrt(tau2_true), size=k)
        obs = rng.normal(true_i, sei)
        iv = compute_intervals(obs, sei, alpha=alpha)
        if not iv["computable"]:
            continue
        new_true = rng.normal(theta_true, math.sqrt(tau2_true))
        for m, lohi in iv["intervals"].items():
            if lohi is None:
                continue
            seen[m] += 1
            if lohi[0] <= new_true <= lohi[1]:
                hit[m] += 1

    out = {}
    for m in hit:
        if seen[m]:
            p = hit[m] / seen[m]
            mc = 3.0 * math.sqrt(max(p * (1 - p), 1e-12) / seen[m])  # 3-sigma
            out[m] = {"coverage": p, "mc_3sigma": mc, "n": seen[m]}
        else:
            out[m] = {"coverage": math.nan, "mc_3sigma": math.nan, "n": 0}
    return {"target": 1 - alpha, "n_sims": n_sims, "seed": seed, "by_method": out}


def report(net: dict) -> dict:
    """Full P0-B report on a network's class-pooled active-vs-placebo effect."""
    from phase1 import data_io
    yi, sei = data_io.active_vs_placebo_sample(net)
    iv = compute_intervals(yi, sei)
    cov = honest_coverage(yi, sei)
    rec = recommend_pi(cov, iv)
    sim = simulate_coverage(iv["theta"], iv["tau2"], sei) if iv["computable"] else None
    return {"k": iv["k"], "theta": iv.get("theta"), "tau2": iv.get("tau2"),
            "intervals": iv, "loo_coverage": cov, "recommendation": rec,
            "known_truth_sim": sim}


def main() -> int:
    from phase1 import data_io
    net = data_io.load_network()
    rep = report(net)
    print("P0-B  HONEST PREDICTION-INTERVAL COVERAGE (class-pooled active vs placebo)\n")
    print(f"  k={rep['k']}  theta={rep['theta']:.4f} (logHR)  tau2={rep['tau2']:.4f}\n")
    iv = rep["intervals"]["intervals"]
    w = rep["intervals"]["widths"]
    print("  Prediction intervals (logHR) and LOO empirical coverage:")
    for m in ("conformal", "standard", "hksj"):
        lo, hi = iv[m]
        c = rep["loo_coverage"].get(m)
        cs = f"{c:.2f}" if c == c else "n/a"  # nan check
        print(f"    {m:9s}  [{lo:+.3f}, {hi:+.3f}]  width={w[m]:.3f}  LOO-coverage={cs}")
    rec = rep["recommendation"]
    print(f"\n  Recommended PI: {rec['recommended']}  (meets nominal {NOMINAL}: {rec['meets_nominal']})")
    if not rec["meets_nominal"]:
        print(f"    -> {rec['note']}")
    sim = rep["known_truth_sim"]
    if sim:
        print(f"\n  Known-truth sim (target {sim['target']}, n={sim['n_sims']}, seed={sim['seed']}):")
        for m, s in sim["by_method"].items():
            print(f"    {m:9s}  coverage={s['coverage']:.3f} +/- {s['mc_3sigma']:.3f} (3 sigma)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
