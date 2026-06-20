# Phase 1 — TDD Plan (the two P0 integrations)

**Date:** 2026-06-20
**Scope:** Implement the two P0 items from `INTEGRATION-MAP.md` on ONE worked NMA dataset, producing one signed capsule that demonstrates *frontier estimator → self-audit verdict → honest PI*. One milestone, checkpoint at end.
**This doc is the plan only.** No code is written until go/no-go is confirmed.

## Definition of done
A re-runnable pipeline + tests such that, for the aact NMA-MACE-in-T2D network:
1. **P0-B** — composite-likelihood/sandwich NMA effects validated vs `netmeta` (R) within tolerance, AND each treatment-vs-reference effect carries a **calibrated PI benchmarked out-of-sample** (LOO + known-truth sim), reporting which of {standard-t, HKSJ, conformal} actually covers — never assuming conformal wins (per `conformal-ma-honest-refutation`).
2. **P0-A** — a machine-checkable **CINeMA-6-domain self-audit verdict** emitted into `assurance.json`, graded Bronze/Silver/Gold per the e156 assurance standard, extending (not replacing) the existing `aact_stats` block.
3. Full test suite green; pass/fail counts reported. No regressions in `advanced-nma-pooling` or `conformal-ma` suites.

## Dataset & gold references (grounded, verified on disk)
- **Working network:** `C:\Projects\aact-cockpit\docs\nma-major-adverse-cardiovascular-events-in-type-2-diabetes\*.json` — 10 study-level contrast rows (`nct`, `yi`, `sei`, `hr/lci/uci`), reference=placebo, k=10. *k=10 is a deliberately honest small-k test for the coverage claim.*
- **R parity gold:** `advanced-nma-pooling` benchmark harness — `external/r/netmeta_runner.R` (+ `multinma_runner.R`), config `configs/example-benchmark.json`.
- **Known-truth gold:** `truth_effects_vs_reference` in the same benchmark config (simulation truth for coverage validation).

## Reuse map (exact seams — reuse, don't re-derive)
| Need | Reuse | File |
|---|---|---|
| AD random-effects NMA fit + full covariance | `NMAFitResult` (`parameter_cov`, `tau`, `contrast()`) | `advanced-nma-pooling/src/nma_pool/models/core_ad.py` |
| Model spec | `ModelSpec` | `…/models/spec.py` |
| R-parity + known-truth validation | benchmark harness | `…/pipelines/run_benchmark.py`, `tests/integration/test_benchmark.py` |
| Conformal / standard / HKSJ PI + OOS coverage | `conformal_prediction_set`, `standard_prediction_interval`, `hksj_prediction_interval`, `heldout_interval_coverage` | `conformal-ma/pipeline.py` |
| Self-audit schema + grading | existing `assurance.json` checks + `aact_stats`; Bronze/Silver/Gold | `aact-cockpit/docs/.../assurance.json`, `e156-assurance-standard` |
| NMA consistency inputs (incoherence) | node-split / design-by-treatment | `allmeta/nma-inconsistency`, `nma-global-inconsistency` |

**Net-new (the synthesis):** (a) sandwich-variance estimator option on the AD NMA; (b) the NMA→conformal adapter (per-contrast study-level extraction + LOO); (c) CINeMA-6-as-rules verdict block + grader. The base estimators and PI primitives are reused verbatim.

---

## Task 0 — prereq preflight (write FIRST, fail closed)
Script `phase1/preflight.py` that asserts, with a specific user-action list on failure:
1. `nma_pool.models.core_ad` + `nma_pool.data.builder` import. ✅ (already verified)
2. `conformal-ma/pipeline.py` functions import. ✅ (verified present)
3. aact NMA JSON loads; **every contrast has `sei > 0` and finite `yi`** (the `sei:0` row must be resolved or excluded — fail closed, do not silently impute). ⚠️ must check.
4. `Rscript` resolves AND `netmeta` installed (`Rscript -e 'library(netmeta)'`); else mark R-parity SKIP with reason (not a silent pass — per verdict-schema lesson).
5. Benchmark config + truth values load.
→ If any of 1–3/5 fail: STOP, emit action list. R (4) may SKIP with explicit reason but the run is then `UNVERIFIED`, not PASS.

## P0-B — calibrated-PI on composite-likelihood/sandwich NMA (TDD)
- **B1 (test-first):** golden test — fit AD NMA on benchmark network, assert effects vs `netmeta` within tol (`1e-6` deterministic per R-validation rule; relax only for MC). Establishes parity before touching variance.
- **B2:** add sandwich/composite-likelihood **variance option** to the AD model (new `ModelSpec` flag, e.g. `variance="sandwich"`); test that point estimates are unchanged and only SEs differ. Document expected small-k under-coverage (88–94%, N1) in the test.
- **B3:** NMA→conformal adapter — extract per-contrast study-level `(yi, sei)` from the EvidenceDataset; reuse `conformal_prediction_set` / `heldout_interval_coverage`. Test on a contrast with known LOO behaviour.
- **B4 (the honest-coverage gate):** for each treatment-vs-reference effect, compute standard-t, HKSJ, and conformal PIs; run `heldout_interval_coverage` (real LOO) + known-truth sim; **assert the reported "recommended PI" is whichever empirically covers at ≥ nominal — NOT hard-coded to conformal.** This is the test that encodes `conformal-ma-honest-refutation` (C1).
- **B5:** guardrails — multiplicative-vs-additive τ² flagged as a spec axis (C4); POTH gate on any rank statement (C5); `sei=0` fails closed (data-handling lesson).

## P0-A — CINeMA-6 machine-checkable self-audit (TDD)
- **A1 (test-first):** schema test — extended `assurance.json` must contain a `cinema6` block with all 6 domains {within-study bias, reporting bias, indirectness, imprecision, heterogeneity, incoherence}, each graded, plus an overall Bronze/Silver/Gold.
- **A2:** compute the 3 *quantitative* domains from the NMA fit: **heterogeneity** (τ² / Q vs df), **imprecision** (CI vs calibrated-PI width from P0-B), **incoherence** (node-split / design-by-treatment p). Test against the existing network's known `tau2`/`consistency` values.
- **A3:** the 3 *structured-input* domains (within-study bias, reporting bias, indirectness) read declared inputs; **fail closed / grade-down on missing required input — never substitute a plausible default** (substitution-on-missing lesson). Keep outputs graded, not binary (risk: CINeMA-as-rules over-claiming).
- **A4:** grader maps 6 domains → Bronze/Silver/Gold per e156 assurance standard; test the boundary cases (any domain "very serious" → caps the grade).
- **A5:** integrate verdict into the capsule export so the published capsule shows the signed self-audit (TruthCert-on-export reuse).

## Validation & acceptance (numerical baselines — version-controlled)
- Estimator: ≤ `1e-6` vs `netmeta` on benchmark network (deterministic).
- Coverage: known-truth sim, 3-sigma Monte-Carlo bounds (`atol≈0.05`), seeded; report empirical coverage of each PI method honestly even if conformal loses.
- Self-audit: golden `assurance.json` snapshot for the MACE network; regression-locked.
- Commit one numerical baseline fixture (per numerical-baseline-contract rule).

## Out of scope (Phase 1 non-goals)
P1/P2 items (NMA spec-grid + weighted-likelihood multiverse, RoBMA bridge, online conformal for living NMA, disease-stage DTA, threshold-analysis witness). Disease-stage DTA and the full multiverse layer wait until the two P0 seams are proven on this one network.

## Risks
- `sei=0` contrast row → resolve source value or exclude with logged reason before any fit (do not impute).
- R/netmeta absent on this box → R-parity SKIP ⇒ run is UNVERIFIED, not PASS; validate via known-truth sim + a pinned numeric fixture instead.
- k=10 small-sample: expect sandwich + conformal to under-cover; that is the *finding to report honestly*, not a bug to hide.
