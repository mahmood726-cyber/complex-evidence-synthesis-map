"""Phase-2 NMA multiverse: spec-curve + weighted-likelihood aggregation + POTH.

A *network spec* applies one analytic choice (tau2 estimator x CI method) to all
active-vs-placebo contrasts. We then:
  1. aggregate each contrast across specs with weighted_likelihood (primary;
     never IV-RE -- C2) and show naive_ivre_pool / naive_concordance as the
     false-robustness contrast;
  2. compute the treatment hierarchy under every spec and gate any "best"
     claim on POTH >= 0.5 (C5).
"""

from __future__ import annotations

from phase1 import bootstrap, data_io
from phase2 import pubbias, ranking, specs

bootstrap.add_spec_collapse()
from spec_collapse import aggregators as AGG  # noqa: E402  (reused aggregators)


def _contrast_inputs(net: dict):
    """Per active treatment: (yi, vi) of its vs-reference studies."""
    out = {}
    for t in data_io.active_treatments(net):
        studies = data_io.studies_for_treatment(net, t)
        if not studies:
            continue
        yi = [s.yi for s in studies]
        vi = [s.sei ** 2 for s in studies]
        out[t] = (yi, vi)
    return out


def report(net: dict, n_mc: int = 20000, seed: int = 20260620) -> dict:
    ref = data_io.reference(net)
    lower_better = bool(net.get("lower_is_better", True))
    inputs = _contrast_inputs(net)
    specs_by_contrast = {t: specs.grid_for_contrast(yi, vi) for t, (yi, vi) in inputs.items()}
    n_specs = len(next(iter(specs_by_contrast.values())))

    # (1) per-contrast aggregation across specs
    per_contrast = {}
    for t, sp in specs_by_contrast.items():
        wl = AGG.weighted_likelihood(sp)
        ivre = AGG.naive_ivre_pool(sp)
        conc = AGG.naive_concordance(sp)
        per_contrast[t] = {
            "weighted_likelihood": {k: wl[k] for k in
                                    ("theta", "ci_low", "ci_high", "significant", "verdict")},
            "naive_ivre_pool": {k: ivre[k] for k in
                                ("theta", "ci_low", "ci_high", "significant", "verdict")},
            "concordance": {k: conc[k] for k in ("pct_significant", "verdict")},
            "ci_width_wl": wl["ci_high"] - wl["ci_low"],
            "ci_width_ivre": ivre["ci_high"] - ivre["ci_low"],
        }

    # (2) hierarchy under each network spec
    per_spec_hier = []
    best_counts: dict[str, int] = {}
    for j in range(n_specs):
        any_spec = next(iter(specs_by_contrast.values()))[j]
        label = f"{any_spec['estimator']}/{any_spec['ci_method']}"
        effects = {ref: (0.0, 0.0)}
        for t, sp in specs_by_contrast.items():
            effects[t] = (sp[j]["theta"], sp[j]["var"])
        h = ranking.hierarchy_report(effects, lower_better, n_mc, seed)
        best = h["reference_order"][0]
        best_counts[best] = best_counts.get(best, 0) + 1
        per_spec_hier.append({"spec": label, "best": best,
                              "poth": round(h["poth"], 4),
                              "informative": h["informative"]})

    # NEW axis (C4): multiplicative-vs-additive AIC choice per contrast
    het_choice = {t: specs.multiplicative_vs_additive(yi, vi)
                  for t, (yi, vi) in inputs.items()}

    # NEW axis (RoBMA-style): publication-bias model-averaging on the k=10
    # network-level active-vs-placebo sample (per-contrast k is too small).
    yi_net, vi_net = data_io.active_vs_placebo_sample(net)
    vi_net = [s ** 2 for s in vi_net]
    pub_bias = pubbias.robma_style(yi_net, vi_net)

    poths = [h["poth"] for h in per_spec_hier]
    # aggregated hierarchy from the weighted-likelihood per-contrast effects
    agg_effects = {ref: (0.0, 0.0)}
    for t in specs_by_contrast:
        wl = AGG.weighted_likelihood(specs_by_contrast[t])
        agg_effects[t] = (wl["theta"], wl["var"])
    agg_hier = ranking.hierarchy_report(agg_effects, lower_better, n_mc, seed)

    return {
        "n_network_specs": n_specs,
        "reference": ref,
        "per_contrast": per_contrast,
        "hierarchy_per_spec": per_spec_hier,
        "best_treatment_distribution": best_counts,
        "poth_min": round(min(poths), 4),
        "poth_max": round(max(poths), 4),
        "het_model_choice": het_choice,
        "pub_bias_robma": pub_bias,
        "aggregated_hierarchy": {
            "order": agg_hier["reference_order"],
            "sucra": {k: round(v, 4) for k, v in agg_hier["sucra"].items()},
            "poth": round(agg_hier["poth"], 4),
            "informative": agg_hier["informative"],
        },
    }


def main() -> int:
    import json
    net = data_io.load_network()
    rep = report(net)
    print("PHASE-2  NMA MULTIVERSE  (%d network specs: %s tau2 x %s CI)\n" % (
        rep["n_network_specs"], "/".join(specs.TAU2_METHODS), "/".join(specs.CI_METHODS)))
    print("Per-contrast aggregation (weighted-likelihood vs the IV-RE cardinal sin):")
    for t, c in rep["per_contrast"].items():
        wl, iv = c["weighted_likelihood"], c["naive_ivre_pool"]
        print(f"  {t:18s} WL  theta={wl['theta']:+.3f} [{wl['ci_low']:+.3f},{wl['ci_high']:+.3f}] "
              f"{wl['verdict']:8s} (width {c['ci_width_wl']:.3f})")
        print(f"  {'':18s} IVRE theta={iv['theta']:+.3f} [{iv['ci_low']:+.3f},{iv['ci_high']:+.3f}] "
              f"{iv['verdict']:8s} (width {c['ci_width_ivre']:.3f})  <- anti-conservative")
    print(f"\nHierarchy robustness across {rep['n_network_specs']} specs:")
    print(f"  best-treatment distribution: {rep['best_treatment_distribution']}")
    print(f"  POTH range: [{rep['poth_min']}, {rep['poth_max']}]")
    ah = rep["aggregated_hierarchy"]
    print(f"  aggregated order: {' > '.join(ah['order'])}")
    print(f"  aggregated POTH = {ah['poth']}  -> hierarchy informative: {ah['informative']}")
    if not ah["informative"]:
        print("  => POTH < 0.5: hierarchy is NON-INFORMATIVE; do NOT claim a 'best' treatment (C5).")

    print("\nMultiplicative-vs-additive axis (C4; switch only if dAIC >= 2):")
    for t, h in rep["het_model_choice"].items():
        print(f"  {t:18s} AIC add={h['aic_additive']:.2f} ({h['best_additive_estimator']}) "
              f"mult={h['aic_multiplicative']:.2f} (phi={h['phi']}) "
              f"dAIC={h['delta_aic_add_minus_mult']:+.2f} -> {h['choice']}")

    pb = rep["pub_bias_robma"]
    print(f"\nRoBMA-style pub-bias model-averaging (network k={pb['k']}, "
          f"underpowered={pb['underpowered']}):")
    for mdl in pb["models"]:
        print(f"  {mdl['method']:10s} theta={mdl['theta']:+.3f}  AIC={mdl['aic']:.2f}  w={mdl['weight']}")
    ma, rw = pb["model_averaged"], pb["raw"]
    print(f"  model-averaged theta={ma['theta']:+.3f} [{ma['ci_low']:+.3f},{ma['ci_high']:+.3f}] "
          f"sig={ma['significant']}  vs raw sig={rw['significant']}")
    print("\n" + json.dumps(rep["aggregated_hierarchy"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
