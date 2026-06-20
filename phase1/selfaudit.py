"""P0-A: CINeMA-6 machine-checkable self-audit verdict for an NMA.

Maps the six CINeMA domains to machine-checkable levels and a Bronze/Silver/Gold
badge (e156 assurance standard). Three domains are computed from the fit
(heterogeneity, imprecision, incoherence); three read declared inputs
(within-study bias, reporting bias, indirectness). Missing structured inputs are
graded as `unassessed -> downgrade`, NEVER substituted with "no concern"
(fail-closed; no plausible-default substitution).

Levels: no_concern < some_concern < major_concern; `unassessed` == downgrade.
Certainty: High > Moderate > Low > Very Low. Badge: Gold=High, Silver=Moderate,
Bronze=Low/Very Low. Any single major_concern caps the badge at Bronze.
"""

from __future__ import annotations

import math

LEVELS = ("no_concern", "some_concern", "major_concern", "unassessed")
_DOWNGRADE = {"no_concern": 0, "some_concern": 1, "major_concern": 2, "unassessed": 1}
CERTAINTY = ("High", "Moderate", "Low", "Very Low")


def _domain(level: str, rationale: str, **metrics) -> dict:
    assert level in LEVELS, level
    return {"level": level, "rationale": rationale, "metrics": metrics}


def assess_heterogeneity(nma: dict) -> dict:
    Q, df, tau2 = float(nma["Q"]), float(nma["df"]), float(nma["tau2"])
    i2 = max(0.0, (Q - df) / Q) if Q > 0 else 0.0
    if i2 > 0.60:
        lvl = "major_concern"
    elif i2 >= 0.30:
        lvl = "some_concern"
    else:
        lvl = "no_concern"
    return _domain(lvl, f"I2={i2:.0%} (Q={Q:.1f}, df={df:.0f}); tau2={tau2:.4f} "
                        f"(I2 is a proportion, not magnitude -- tau2 reported alongside)",
                   i2=i2, tau2=tau2)


def assess_imprecision(nma: dict, recommended_pi: tuple[float, float] | None) -> dict:
    """Concern if relative-effect CIs cross the null; major if the prediction
    interval spans appreciable benefit AND appreciable harm (HR<0.8 and >1.25)."""
    rel = nma["rel_to_ref"]
    crosses = [t for t, v in rel.items()
               if v["lo"] <= 1.0 <= v["hi"] and t != nma["reference"]]
    pi_spans_both = False
    if recommended_pi is not None:
        lo_hr, hi_hr = math.exp(recommended_pi[0]), math.exp(recommended_pi[1])
        pi_spans_both = lo_hr < 0.80 and hi_hr > 1.25
    if pi_spans_both:
        lvl = "major_concern"
    elif crosses:
        lvl = "some_concern"
    else:
        lvl = "no_concern"
    return _domain(lvl, f"{len(crosses)} of {len(rel) - 1} active contrasts have a 95% CI "
                        f"crossing HR=1; recommended PI spans benefit&harm: {pi_spans_both}",
                   n_crossing_null=len(crosses), pi_spans_benefit_and_harm=pi_spans_both)


def assess_incoherence(nma: dict) -> dict:
    c = nma.get("consistency") or {}
    assessable = c.get("assessable", False)
    inconsistent = c.get("inconsistent", False)
    if not assessable:
        return _domain("some_concern",
                       "no closed loops (star network) -> inconsistency is UNDETECTABLE, "
                       "not demonstrated absent; cannot rule out (advanced-stats NMA rule)",
                       assessable=False)
    if inconsistent:
        return _domain("major_concern", f"design-by-treatment/node-split flags inconsistency "
                                        f"(min_p={c.get('min_p')})", **c)
    return _domain("no_concern", f"consistency assessed and not rejected (min_p={c.get('min_p')})", **c)


def assess_indirectness(net: dict) -> dict:
    sa = (net.get("self_audit") or {}).get("aact_stats") or {}
    t = sa.get("transitivity")
    mapping = {"pass": "no_concern", "warn": "some_concern", "fail": "major_concern"}
    if t in mapping:
        return _domain(mapping[t], f"transitivity assessment = {t!r}", transitivity=t)
    return _domain("unassessed", "no transitivity assessment provided -> downgrade (not assumed met)")


def assess_within_study_bias(net: dict) -> dict:
    rob = net.get("risk_of_bias")
    if not rob:
        return _domain("unassessed",
                       "no per-study risk-of-bias provided -> graded DOWN, not assumed low "
                       "(fail-closed: no plausible-default substitution)")
    # if provided, expect {'high': n, 'some': n, 'low': n}
    high = rob.get("high", 0)
    if high:
        return _domain("major_concern", f"{high} studies at high risk of bias", **rob)
    return _domain("some_concern" if rob.get("some") else "no_concern",
                   "risk-of-bias provided", **rob)


def assess_reporting_bias(net: dict) -> dict:
    rep = net.get("reporting_bias")
    if not rep:
        src = (net.get("provenance") or {}).get("source", "unknown")
        return _domain("unassessed",
                       f"no reporting-bias assessment; source={src!r} (registry-derived data has "
                       f"known trial-to-publication linkage gaps) -> downgrade, not assumed absent")
    return _domain(rep.get("level", "some_concern"), "reporting-bias assessment provided", **rep)


def grade(domains: dict) -> dict:
    total = sum(_DOWNGRADE[d["level"]] for d in domains.values())
    has_major = any(d["level"] == "major_concern" for d in domains.values())
    drop = min(total, 3)
    certainty = CERTAINTY[drop]
    badge = {"High": "Gold", "Moderate": "Silver", "Low": "Bronze", "Very Low": "Bronze"}[certainty]
    # any major concern caps the badge at Bronze regardless of total
    if has_major and badge in ("Gold", "Silver"):
        badge, certainty = "Bronze", "Low"
    return {"certainty": certainty, "badge": badge,
            "downgrade_points": total, "has_major_concern": has_major}


def cinema6_verdict(net: dict, recommended_pi: tuple[float, float] | None = None) -> dict:
    nma = net["nma"]
    nma = {**nma, "reference": net["reference"]}
    domains = {
        "heterogeneity": assess_heterogeneity(nma),
        "imprecision": assess_imprecision(nma, recommended_pi),
        "incoherence": assess_incoherence(nma),
        "indirectness": assess_indirectness(net),
        "within_study_bias": assess_within_study_bias(net),
        "reporting_bias": assess_reporting_bias(net),
    }
    return {"cinema6": domains, "grade": grade(domains)}


def merge_into_assurance(existing: dict, verdict: dict) -> dict:
    """Extend an existing assurance.json dict; never drop prior keys."""
    out = dict(existing)
    out["cinema6"] = verdict["cinema6"]
    out["cinema6_grade"] = verdict["grade"]
    return out


def main() -> int:
    from phase1 import coverage, data_io
    net = data_io.load_network()
    rep = coverage.report(net)
    rec_name = rep["recommendation"]["recommended"]
    rec_pi = rep["intervals"]["intervals"].get(rec_name)
    verdict = cinema6_verdict(net, rec_pi)
    print("P0-A  CINeMA-6 SELF-AUDIT VERDICT\n")
    for name, d in verdict["cinema6"].items():
        print(f"  {name:18s} {d['level']:14s} {d['rationale']}")
    g = verdict["grade"]
    print(f"\n  => Certainty: {g['certainty']}  |  Badge: {g['badge']}  "
          f"(downgrades={g['downgrade_points']}, major={g['has_major_concern']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
