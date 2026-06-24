"""RoBMA-style publication-bias axis (portable analog of RoBMA's Bayesian
model-averaging over pub-bias models).

RoBMA proper averages {effect, heterogeneity, pub-bias} model components weighted
by marginal likelihood; it is a heavy Bayesian/MCMC package and is NOT installed
in the local R, so this is the deterministic portable analog: enumerate the
pub-bias-adjustment models {raw, trim-and-fill, PET-PEESE}, weight each by an
AIC-approximated marginal likelihood, and combine with the spec-collapse
weighted_likelihood mixture (never IV-RE). RoBMA-in-R remains a future cross-check.

HONESTY: small-study/selection methods need k>=10 for any power; applied here to
the k=10 network-level active-vs-placebo sample they are underpowered and reported
as sensitivity, never as a primary correction.
"""

from __future__ import annotations

import math

import numpy as np

from phase1 import bootstrap

bootstrap.add_spec_collapse()
from spec_collapse import aggregators as AGG   # noqa: E402
from spec_collapse import engine as E          # noqa: E402


def _re(yi, vi):
    tau2 = E.tau2_dl(list(yi), list(vi))
    theta, var, _, _ = E.re_pool(list(yi), list(vi), tau2)
    return theta, var, tau2


def spec_raw(yi, vi) -> dict:
    theta, var, tau2 = _re(yi, vi)
    return {"method": "raw", "theta": theta, "var": var, "tau2": tau2, "k": len(yi),
            "loglik": E._re_loglik(list(yi), list(vi), theta, tau2), "n_params": 2}


def spec_trim_fill(yi, vi) -> dict:
    yf, vf = E.trim_and_fill(list(yi), list(vi), E.tau2_dl)
    theta, var, tau2 = _re(yf, vf)
    k0 = len(yf) - len(yi)
    return {"method": "trim_fill", "theta": theta, "var": var, "tau2": tau2,
            "k": len(yf), "k0_imputed": k0,
            "loglik": E._re_loglik(list(yf), list(vf), theta, tau2), "n_params": 2}


def spec_pet_peese(yi, vi) -> dict:
    """Conditional PET-PEESE (Stanley-Doucouliagos): PET first; if PET rejects the
    no-effect null at one-sided p<0.10, report the PEESE intercept instead."""
    k = len(yi)
    yi = np.asarray(yi, float)
    sei = np.sqrt(np.asarray(vi, float))
    w = 1.0 / np.asarray(vi, float)
    if k < 3:
        s = spec_raw(yi, vi.tolist() if hasattr(vi, "tolist") else list(vi))
        s["method"] = "pet_peese"; s["note"] = "k<3: fell back to raw"; s["n_params"] = 2
        return s

    def _wls(x_extra):
        X = np.column_stack([np.ones(k), x_extra])
        W = np.diag(w)
        xtwx = X.T @ W @ X
        cov = np.linalg.inv(xtwx)
        beta = cov @ X.T @ W @ yi
        return beta, cov

    # PET: regress on SE; intercept = limit effect as precision -> infinity
    from scipy import stats as sp
    beta_pet, cov_pet = _wls(sei)
    b0, se0 = beta_pet[0], math.sqrt(max(cov_pet[0, 0], 0.0))
    t = abs(b0 / se0) if se0 > 0 else 0.0
    p = 2 * (1 - sp.t.cdf(t, k - 2))
    if p < 0.10:  # effect present -> PEESE (regress on variance)
        beta, cov = _wls(np.asarray(vi, float))
        method = "peese"
    else:
        beta, cov = beta_pet, cov_pet
        method = "pet"
    theta = float(beta[0]); var = float(max(cov[0, 0], 0.0))
    # loglik at adjusted theta with DL tau2 on the original data
    tau2 = E.tau2_dl(list(yi), list(vi))
    return {"method": "pet_peese", "submethod": method, "theta": theta, "var": var,
            "tau2": tau2, "k": k,
            "loglik": E._re_loglik(list(yi), list(vi), theta, tau2), "n_params": 3}


def robma_style(yi, vi, cl: float = 0.95) -> dict:
    """Model-average {raw, trim_fill, PET-PEESE} by AIC weights, combine via the
    spec-collapse weighted_likelihood mixture. Returns the averaged interval plus
    the raw (unadjusted) interval for contrast."""
    specs = [spec_raw(yi, vi), spec_trim_fill(yi, vi), spec_pet_peese(yi, vi)]
    aics = [-2.0 * s["loglik"] + 2.0 * s["n_params"] for s in specs]
    amin = min(aics)
    weights = [math.exp(-0.5 * (a - amin)) for a in aics]
    averaged = AGG.weighted_likelihood(specs, cl=cl, weights=weights)
    raw = specs[0]
    z = 1.959963984540054
    raw_lo = raw["theta"] - z * math.sqrt(raw["var"])
    raw_hi = raw["theta"] + z * math.sqrt(raw["var"])
    sw = sum(weights)
    return {
        "models": [{"method": s["method"], "theta": round(s["theta"], 4),
                    "aic": round(a, 3), "weight": round(wi / sw, 3)}
                   for s, a, wi in zip(specs, aics, weights)],
        "model_averaged": {"theta": round(averaged["theta"], 4),
                           "ci_low": round(averaged["ci_low"], 4),
                           "ci_high": round(averaged["ci_high"], 4),
                           "significant": bool(averaged["significant"])},
        "raw": {"theta": round(raw["theta"], 4), "ci_low": round(raw_lo, 4),
                "ci_high": round(raw_hi, 4), "significant": bool(raw_lo > 0 or raw_hi < 0)},
        "k": len(yi),
        "underpowered": len(yi) < 10,
    }
