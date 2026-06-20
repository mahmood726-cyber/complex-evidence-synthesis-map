# Complex-Evidence Synthesis — Method-Scan & Integration Map

A design project that fuses three existing assurance/robustness strands with the
2024–2026 frontier of NMA / DTA / complex-evidence meta-analysis methods, to define a
**verifiable complex-evidence synthesis**: any frontier estimator wrapped in a
self-audit verdict, an honestly-calibrated prediction interval, and a multiverse
specification curve.

> The synthesis is the **wrapper**, not a new estimator.

## Status
- **Phase 0 — method scan + integration map:** complete → [`docs/INTEGRATION-MAP.md`](docs/INTEGRATION-MAP.md)
- **Phase 1 — two P0 integrations (TDD plan):** scoped → [`docs/PHASE-1-PLAN.md`](docs/PHASE-1-PLAN.md)
- Implementation: not started in this repo yet (reuses `advanced-nma-pooling`, `conformal-ma`, `aact-cockpit`, e156 assurance standard).

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
