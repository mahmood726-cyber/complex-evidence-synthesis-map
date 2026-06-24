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

import math

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
        "het_model": "additive",
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


def _mult_loglik(yi, vi, theta, phi) -> float:
    """Gaussian log-likelihood under multiplicative variance phi * v_i."""
    return -0.5 * sum(math.log(2 * math.pi * phi * v) + (y - theta) ** 2 / (phi * v)
                      for y, v in zip(yi, vi))


def pool_multiplicative(yi, vi, cl: float = 0.95) -> dict:
    """Multiplicative-heterogeneity model (Thompson-Sharp): fixed-effect point
    estimate with the variance scaled by the overdispersion phi = max(1, Q/(k-1)).
    An alternative to additive tau^2; treated here as a forking-path axis (C4).
    """
    import scipy.stats as sp
    k = len(yi)
    w = [1.0 / v for v in vi]
    sw = sum(w)
    theta = sum(wi * y for wi, y in zip(w, yi)) / sw
    Q = sum(wi * (y - theta) ** 2 for wi, y in zip(w, yi))
    phi = max(1.0, Q / (k - 1)) if k > 1 else 1.0
    var = phi / sw
    tcrit = sp.t.ppf(0.5 + cl / 2, max(1, k - 1))
    half = tcrit * math.sqrt(var)
    lo, hi = theta - half, theta + half
    return {
        "estimator": "MULT",
        "het_model": "multiplicative",
        "ci_method": "mult-t",
        "theta": theta,
        "var": var,
        "phi": phi,
        "k": k,
        "ci_low": lo,
        "ci_high": hi,
        "loglik": _mult_loglik(yi, vi, theta, phi),
        "significant": (lo > 0 or hi < 0),
    }


def grid_for_contrast(yi, vi, cl: float = 0.95) -> list[dict]:
    """Full spec grid: additive (tau2_method x ci_method) + multiplicative."""
    specs = []
    for tm in TAU2_METHODS:
        for cm in CI_METHODS:
            specs.append(pool_one(yi, vi, tm, cm, cl))
    specs.append(pool_multiplicative(yi, vi, cl))      # multiplicative axis
    return specs


def multiplicative_vs_additive(yi, vi, cl: float = 0.95) -> dict:
    """C4 AIC comparison: best additive RE vs multiplicative (both 2-parameter).
    Switch to multiplicative only if it wins by AIC >= 2."""
    add = [pool_one(yi, vi, tm, "Wald", cl) for tm in ("DL", "PM", "REML")]
    best_add = max(add, key=lambda s: s["loglik"])
    mult = pool_multiplicative(yi, vi, cl)
    aic_add = -2 * best_add["loglik"] + 4
    aic_mult = -2 * mult["loglik"] + 4
    delta = aic_add - aic_mult                          # >0 favours multiplicative
    if delta >= 2:
        choice = "multiplicative"
    elif delta <= -2:
        choice = "additive"
    else:
        choice = "indistinguishable"
    return {
        "aic_additive": round(aic_add, 3), "best_additive_estimator": best_add["estimator"],
        "aic_multiplicative": round(aic_mult, 3), "phi": round(mult["phi"], 3),
        "delta_aic_add_minus_mult": round(delta, 3), "choice": choice,
    }
