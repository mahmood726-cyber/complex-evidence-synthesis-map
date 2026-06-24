"""Loop-containing NMA: generalise beyond the aact star network.

The aact network is a star (every active vs placebo), so it has NO closed loops
-> inconsistency is UNDETECTABLE and CINeMA incoherence can only be graded
"some_concern" (cannot rule out). Here we build an A/B/C triangle with direct
A-B, A-C and B-C evidence, which DOES contain a loop, so:
  - core_ad fits using direct + indirect evidence (a real NMA, not pairwise pools);
  - a node-split contrast (direct B-C vs indirect B-C via A) makes incoherence
    ASSESSABLE -> the CINeMA incoherence domain becomes a computed verdict.

All randomness is seeded (numpy default_rng); generic pseudo-arm reconstruction
(value 0 / value yi, se sei/sqrt2) feeds advanced-nma-pooling core_ad.
"""

from __future__ import annotations

import math

import numpy as np

from phase1 import bootstrap

bootstrap.add_advanced_nma_pooling()
from nma_pool.data.builder import DatasetBuilder      # noqa: E402
from nma_pool.models.core_ad import ADNMAPooler        # noqa: E402
from nma_pool.models.spec import ModelSpec             # noqa: E402

OUTCOME = "y"
REF = "A"


def make_triangle(d_b: float = 0.5, d_c: float = 0.9, inconsistency: float = 0.0,
                  n_per: int = 4, se: float = 0.12, seed: int = 20260624) -> list[dict]:
    """Triangle contrasts. True A->B = d_b, A->C = d_c; consistent B->C = d_c-d_b.
    `inconsistency` shifts the direct B-C evidence away from the loop-implied value.
    Each contrast dict: {t1, t2, yi, sei} with yi the t2-vs-t1 effect."""
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    plan = [("A", "B", d_b), ("A", "C", d_c), ("B", "C", (d_c - d_b) + inconsistency)]
    for t1, t2, true in plan:
        for _ in range(n_per):
            rows.append({"t1": t1, "t2": t2,
                         "yi": float(rng.normal(true, se)), "sei": se})
    return rows


def build_dataset(contrasts: list[dict], ref: str = REF):
    studies, arms, outcomes = [], [], []
    for i, c in enumerate(contrasts):
        sid = f"s{i:03d}"
        se_arm = c["sei"] / math.sqrt(2.0)
        studies.append({"study_id": sid, "design": "rct", "year": 2020,
                        "source_id": sid, "rob_domain_summary": "unknown"})
        # arm "0" = t1 (baseline), arm "1" = t2  ->  contrast t2 - t1 = yi
        arms.append({"study_id": sid, "arm_id": "0", "treatment_id": c["t1"],
                     "n": 100, "dose": None, "components": [c["t1"]]})
        arms.append({"study_id": sid, "arm_id": "1", "treatment_id": c["t2"],
                     "n": 100, "dose": None, "components": [c["t2"]]})
        outcomes.append({"study_id": sid, "arm_id": "0", "outcome_id": OUTCOME,
                         "measure_type": "continuous", "value": 0.0, "se": se_arm})
        outcomes.append({"study_id": sid, "arm_id": "1", "outcome_id": OUTCOME,
                         "measure_type": "continuous", "value": c["yi"], "se": se_arm})
    return DatasetBuilder().from_records(studies=studies, arms=arms, outcomes_ad=outcomes)


def fit(contrasts: list[dict], ref: str = REF, variance: str = "model"):
    ds = build_dataset(contrasts, ref)
    spec = ModelSpec(outcome_id=OUTCOME, measure_type="continuous",
                     reference_treatment=ref, random_effects=True, variance=variance)
    return ADNMAPooler().fit(ds, spec)


def _pool_direct(contrasts, t1, t2):
    """Inverse-variance pool of the direct t1-t2 studies (sign: t2 - t1)."""
    ys, vs = [], []
    for c in contrasts:
        if c["t1"] == t1 and c["t2"] == t2:
            ys.append(c["yi"]); vs.append(c["sei"] ** 2)
        elif c["t1"] == t2 and c["t2"] == t1:
            ys.append(-c["yi"]); vs.append(c["sei"] ** 2)
    if not ys:
        return None
    w = [1.0 / v for v in vs]
    sw = sum(w)
    return sum(wi * y for wi, y in zip(w, ys)) / sw, 1.0 / sw


def node_split_bc(contrasts: list[dict]) -> dict:
    """Direct B-C vs indirect B-C (via A): the consistency check a star cannot do."""
    from scipy import stats as sp
    direct = _pool_direct(contrasts, "B", "C")
    ab = _pool_direct(contrasts, "A", "B")   # A->B
    ac = _pool_direct(contrasts, "A", "C")   # A->C
    if direct is None or ab is None or ac is None:
        return {"assessable": False}
    d_dir, v_dir = direct
    d_ind, v_ind = (ac[0] - ab[0]), (ac[1] + ab[1])   # B->C = (A->C) - (A->B)
    diff = d_dir - d_ind
    se = math.sqrt(v_dir + v_ind)
    z = float(diff / se) if se > 0 else 0.0
    p = float(2 * (1 - sp.norm.cdf(abs(z))))
    return {"assessable": True, "direct_bc": float(d_dir), "indirect_bc": float(d_ind),
            "diff": float(diff), "z": z, "p": p, "inconsistent": bool(p < 0.05)}


def main() -> int:
    for label, inc in (("consistent", 0.0), ("inconsistent", 0.6)):
        rows = make_triangle(inconsistency=inc)
        fm = fit(rows)
        ns = node_split_bc(rows)
        print(f"[{label}] core_ad effects vs A: "
              f"B={fm.treatment_effects['B']:+.3f} C={fm.treatment_effects['C']:+.3f} "
              f"(tau={fm.tau:.3f})")
        print(f"           node-split B-C: direct={ns['direct_bc']:+.3f} "
              f"indirect={ns['indirect_bc']:+.3f} p={ns['p']:.3f} "
              f"inconsistent={ns['inconsistent']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
