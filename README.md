# Complex-Evidence Synthesis — Method-Scan & Integration Map

A design project that fuses three existing assurance/robustness strands with the
2024–2026 frontier of NMA / DTA / complex-evidence meta-analysis methods, to define a
**verifiable complex-evidence synthesis**: any frontier estimator wrapped in a
self-audit verdict, an honestly-calibrated prediction interval, and a multiverse
specification curve.

> The synthesis is the **wrapper**, not a new estimator.

## Status
- **Phase 0 — method scan + integration map:** complete → [`docs/INTEGRATION-MAP.md`](docs/INTEGRATION-MAP.md)
- **Phase 1 — two P0 integrations:** TDD plan → [`docs/PHASE-1-PLAN.md`](docs/PHASE-1-PLAN.md); first increment **implemented, 18 tests green**:
  - Task 0 `phase1/preflight.py` — fail-closed data checks; sibling-repo + R/netmeta SKIP-with-reason.
  - **P0-B** `phase1/coverage.py` — reuses `conformal-ma` PI primitives verbatim; `recommend_pi` selects by empirical out-of-sample coverage and **never defaults to conformal**; known-truth simulator is the R-free validation path.
  - **P0-A** `phase1/selfaudit.py` — CINeMA-6 machine-checkable verdict → Bronze/Silver/Gold; missing inputs grade `unassessed → downgrade`, never "no concern".
  - `phase1/verdict.py` — combined capsule-ready verdict; version-controlled baseline at `tests/fixtures/verdict_baseline.json`.
- Reuses `advanced-nma-pooling`, `conformal-ma`, `aact-cockpit`, e156 assurance standard. Run: `python -m phase1.preflight`, `python -m phase1.verdict`, `python -m pytest`.

### First worked result (aact NMA-MACE-in-T2D, k=10) — *UNVERIFIED* (netmeta SKIP on this box)
Honest, non-hyped finding: on real-data LOO all three PIs cover 0.90 (< nominal 0.95) — conformal earns nothing over standard/HKSJ; under a correctly-specified normal model conformal is conservative (0.967) while standard/HKSJ under-cover (~0.92). Self-audit grade: **Bronze / Very Low** (high heterogeneity, CIs cross null, RoB & reporting unassessed). No free lunch.

## The three anchor strands (reused, not rebuilt)
1. **Self-auditing / TruthCert** — internal-consistency checks, signed capsules (e156 assurance standard).
2. **Conformal / PI honest-coverage** — `conformal-ma` (with its own finding: conformal *under-covers* at small k; standard PI wins out-of-sample).
3. **Spec-collapse / multiverse** — `spec-collapse-atlas` weighted-likelihood aggregator (never IV-RE-pool specs).

## What the map covers
Frontier methods scanned and mapped onto portfolio engines: composite-likelihood +
sandwich NMA, class-effects NMA, CINeMA confidence, RoBMA model-averaging,
multiple-threshold & disease-stage DTA, and the conformal frontier. See the integration
map for the fusion matrix and the prioritised roadmap; see the Phase-1 plan for the
grounded TDD task list and acceptance thresholds.

## License
MIT
