"""B2: wire advanced-nma-pooling's core_ad estimator + its new sandwich-variance
option into the synthesis, on the (contrast-level) aact network.

core_ad is arm-level, the aact network is contrast-level, so we reconstruct EXACT
pseudo-arms: for a study with active-vs-reference log-effect yi and SE sei, a
reference arm (value 0, se sei/sqrt2) and an active arm (value yi, se sei/sqrt2)
reproduce the contrast mean yi and variance sei^2 exactly. This is a standard
contrast-input reparameterization, not fabricated clinical data.

We then fit with variance='model' and variance='sandwich' and expose both SEs:
the sandwich is the Lu/Ades composite-likelihood robust variance that
under-covers at small contrast counts (the N1 frontier caveat, demonstrated).
"""

from __future__ import annotations

import math

from phase1 import bootstrap, data_io

bootstrap.add_advanced_nma_pooling()
from nma_pool.data.builder import DatasetBuilder      # noqa: E402
from nma_pool.models.core_ad import ADNMAPooler        # noqa: E402
from nma_pool.models.spec import ModelSpec             # noqa: E402

OUTCOME = "mace"


def build_dataset(net: dict):
    ref = data_io.reference(net)
    studies, arms, outcomes = [], [], []
    for i, c in enumerate(data_io.contrasts(net)):
        sid = c.nct or f"s{i}"
        if c.t1 == ref:          # row is reference-vs-active -> flip to active-vs-ref
            active, yi = c.t2, -c.yi
        else:
            active, yi = c.t1, c.yi
        se_arm = c.sei / math.sqrt(2.0)
        studies.append({"study_id": sid, "design": "rct", "year": 2015,
                        "source_id": sid, "rob_domain_summary": "unknown"})
        # arm_id "0" sorts first -> reference is the baseline arm
        arms.append({"study_id": sid, "arm_id": "0", "treatment_id": ref,
                     "n": 100, "dose": None, "components": [ref]})
        arms.append({"study_id": sid, "arm_id": "1", "treatment_id": active,
                     "n": 100, "dose": None, "components": [active]})
        outcomes.append({"study_id": sid, "arm_id": "0", "outcome_id": OUTCOME,
                         "measure_type": "continuous", "value": 0.0, "se": se_arm})
        outcomes.append({"study_id": sid, "arm_id": "1", "outcome_id": OUTCOME,
                         "measure_type": "continuous", "value": yi, "se": se_arm})
    return DatasetBuilder().from_records(studies=studies, arms=arms, outcomes_ad=outcomes)


def fit(net: dict, variance: str = "model", random_effects: bool = True):
    ds = build_dataset(net)
    spec = ModelSpec(outcome_id=OUTCOME, measure_type="continuous",
                     reference_treatment=data_io.reference(net),
                     random_effects=random_effects, variance=variance)
    return ADNMAPooler().fit(ds, spec)


def compare(net: dict | None = None) -> dict:
    net = net or data_io.load_network()
    fm = fit(net, "model")
    fs = fit(net, "sandwich")
    by = {}
    for t in fm.parameter_treatments:
        by[t] = {
            "effect": fm.treatment_effects[t],
            "se_model": fm.treatment_ses[t],
            "se_sandwich": fs.treatment_ses[t],
            "se_ratio_sandwich_over_model": (fs.treatment_ses[t] / fm.treatment_ses[t]
                                             if fm.treatment_ses[t] > 0 else math.nan),
        }
    return {"tau": fm.tau, "n_studies": fm.n_studies, "by_treatment": by}


def main() -> int:
    net = data_io.load_network()
    rep = compare(net)
    print(f"B2  core_ad NMA (shared tau={rep['tau']:.4f}, {rep['n_studies']} contrasts)\n")
    print(f"  {'treatment':18s} {'effect':>9s} {'SE(model)':>10s} {'SE(sandwich)':>13s} {'ratio':>7s}")
    for t, d in rep["by_treatment"].items():
        print(f"  {t:18s} {d['effect']:+9.4f} {d['se_model']:10.4f} "
              f"{d['se_sandwich']:13.4f} {d['se_ratio_sandwich_over_model']:7.3f}")
    print("\n  Sandwich/model SE ratio != 1 demonstrates the robust-variance adjustment;")
    print("  ratios < 1 are the small-contrast-count under-coverage caveat (Lu/Ades).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
