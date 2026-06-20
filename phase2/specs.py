"""Enumerate the NMA forking-path spec grid for each active-vs-reference contrast.

The aact network is a star (all actives vs placebo), so the NMA decomposes into
independent pairwise pools -- one per active treatment. A *specification* is a
choice of:
  - heterogeneity model / tau2 estimator: FE (tau2=0), DL, PM, REML
  - CI method: Wald, HKSJ
(multiplicative-vs-additive RE is represented by the HKSJ q>=1 scaling, which is
the multiplicative variance inflation; documented as axis, per C4.)

Each spec returns the scalar estimand for that contrast (logHR vs reference) with
the fields the spec-collapse weighted_likelihood aggregator consumes:
{theta, var, k, loglik, significant, estimator, ci_method}.

All pooling/tau2/loglik primitives are REUSED verbatim from spec_collapse.engine.
"""

from __future__ import annotations

from phase1 import bootstrap

bootstrap.add_spec_collapse()
from spec_collapse import engine as E  # noqa: E402  (reused pooling primitives)

TAU2_METHODS = ("FE", "DL", "PM", "REML")
CI_METHODS = ("Wald", "HKSJ")


def _tau2(method: str, yi, vi) -> float:
    if method == "FE":
        return 0.0
    if method == "DL":
        return E.tau2_dl(yi, vi)
    if method == "PM":
        return E.tau2_pm(yi, vi)
    if method == "REML":
        return E.tau2_reml(yi, vi)
    raise ValueError(method)


def pool_one(yi, vi, tau2_method: str, ci_method: str, cl: float = 0.95) -> dict:
    """One specification's pooled estimate for a single contrast."""
    k = len(yi)
    tau2 = _tau2(tau2_method, yi, vi)
    theta, var_wald, _, _ = E.re_pool(yi, vi, tau2)
    if ci_method == "HKSJ":
        lo, hi, var = E.ci_hksj(yi, vi, theta, tau2, cl)
    else:
        lo, hi, var = E.ci_wald(theta, var_wald, cl)
    loglik = E._re_loglik(yi, vi, theta, tau2)
    return {
        "estimator": tau2_method,
        "ci_method": ci_method,
        "theta": theta,
        "var": var,
        "tau2": tau2,
        "k": k,
        "ci_low": lo,
        "ci_high": hi,
        "loglik": loglik,
        "significant": (lo > 0 or hi < 0),
    }


def grid_for_contrast(yi, vi, cl: float = 0.95) -> list[dict]:
    """Full spec grid (tau2_method x ci_method) for one contrast."""
    specs = []
    for tm in TAU2_METHODS:
        for cm in CI_METHODS:
            specs.append(pool_one(yi, vi, tm, cm, cl))
    return specs
