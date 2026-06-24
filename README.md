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

- **Phase 2 — multiverse layer:** implemented (`phase2/`):
  - `specs.py` — NMA forking-path grid (FE/DL/PM/REML τ² × Wald/HKSJ CI), reusing `spec_collapse.engine` pooling primitives verbatim.
  - `multiverse.py` — per-contrast aggregation with `weighted_likelihood` (primary; **never IV-RE — C2**) vs `naive_ivre_pool` (the labelled cardinal sin) for contrast; treatment hierarchy under every spec.
  - `ranking.py` — SUCRA + probability-of-best + **POTH** (Wigle 2025), gating any "best treatment" claim on POTH ≥ 0.5 (**C5**).
  - **B1 parity CLOSED:** `validate_r.py` + `external/r/parity.R` — pooling backbone matches `metafor` to **7e-07** (R 4.6.0).
  - **Extension axes:** `specs.py` adds a **multiplicative-NMA** model (Thompson–Sharp φ) as a forking-path axis with the **C4 ΔAIC≥2 switch rule** (`multiplicative_vs_additive`); `pubbias.py` adds a **RoBMA-style** publication-bias axis (raw / trim-fill / PET-PEESE) model-averaged by marginal-likelihood (AIC) weights — the portable analog of RoBMA's Bayesian model-averaging. Findings: all contrasts AIC-indistinguishable additive-vs-multiplicative (GLP-1 φ≈7.6); pub-bias adjustment leaves the conclusion non-significant (PET-PEESE's sign flip down-weighted by poor fit).
- **Generalization & cross-checks** (`phase2/`):
  - `loop_network.py` — **loop-containing NMA** (A/B/C triangle): `core_ad` fits with direct + indirect evidence and a **node-split** consistency test makes CINeMA incoherence *assessable* (a star network cannot) — recovers truth on a consistent network, **detects injected inconsistency** (p<0.001, τ inflated).
  - `dta_stages.py` — **disease-stage DTA (D4)**: combines stage-specific and merged-stage sensitivity (Derezea/Welton/Jones 2026); include-merged is a forking-path axis (**sharpens both per-stage SEs**); stage-closure + monotonicity self-audit. Known-truth recovery validated.
  - `validate_robma.py` + `external/r/robma.R` — **RoBMA-in-R cross-check** of the portable pub-bias averaging; skips-with-reason when **JAGS** (RoBMA's external runtime) is absent, so it runs as soon as JAGS≥4.3.1 is installed.

### Worked results (aact NMA-MACE-in-T2D, k=10) — now **VERIFIED** (metafor parity passes)
- **Coverage (P0-B):** real-data LOO all three PIs cover 0.90 (< nominal 0.95) — conformal earns nothing over standard/HKSJ; known-truth sim shows conformal conservative (0.967) vs standard/HKSJ under-covering (~0.92). No free lunch.
- **Self-audit (P0-A):** **Bronze / Very Low** (I²=73%, CIs cross null, RoB & reporting unassessed).
- **Multiverse (Phase 2):** naive IV-RE pooling calls GLP-1 & SGLT2 vs placebo *"robust"*; weighted-likelihood (correct) calls both *"fragile"* — IV-RE narrows the CI ~6× and manufactures significance. DPP-4 tops the order in all 8 specs, yet aggregated **POTH = 0.21 < 0.5 → hierarchy non-informative**: leader-stable but the full ranking is untrustworthy. Don't claim a "best" treatment.

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
