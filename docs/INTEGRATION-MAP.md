# Complex-Evidence Synthesis — Method-Scan & Integration Map

**Date:** 2026-06-20
**Status:** Phase 0 deliverable — *method scan + integration map only* (no code in this pass).
**Topic scope:** NMA / DTA / complex evidence.
**Anchor strands (the "my methods" half of the fusion):**
1. **Self-auditing / TruthCert** — e156 assurance standard, signed capsules, internal-consistency checks.
2. **Conformal / PI honest-coverage** — `conformal-ma`, allmeta PI (`t_{k-1}`), repro-floor.
3. **Spec-collapse / multiverse** — `spec-collapse-atlas` weighted-likelihood aggregator, `fragility-atlas`.

## Portfolio recon (required disclosure)

- Active manifest (`C:\Users\mahmo\code\ProjectIndex\agent-records\restart-manifest.json`) returned only 2 token-only hits (`fragility-atlas`, `ma-workbench`) for the topic — it is the **sparse/sample index and is stale relative to disk**. Do not read its silence as "no related work."
- On-disk recon (authoritative for this map) found the real reuse base:
  - `C:\Projects\allmeta\{nma, bayesian-nma, component-nma, multiplicative-nma, nma-inconsistency, nma-global-inconsistency, multi-outcome-nma, nma-meta-reg, transported-nma, nma-dose-response-app, dta-sroc}`
  - `C:\Projects\truth-recovery-bench` (pairwise→NMA→DTA→dose-response; DTA Reitsma matches `mada` 1e-6)
  - `C:\Projects\spec-collapse-atlas`, `C:\Projects\conformal-ma`, `C:\Projects\fragility-atlas`
  - `C:\Projects\e156\flagship\{nma, dta-capsule.html, grade-capsule.html, ...}`
  - standalone: `denominator-calibrated-living-nma`, `dta-floor-atlas`, `advanced-nma-pooling`, `component-nma`
- **Reused vs net-new** is itemised per integration in §4. Net-new across the board = the *assurance/coverage/multiverse wrappers*, not the base estimators.

---

## 1. The thesis (what the "new synthesis" actually is)

The frontier 2024–2026 complex-evidence methods are strong at **point estimation and model flexibility** but uniformly weak on three things — and those three things are *exactly* your three anchor strands:

| Frontier method delivers… | …but is silent on | Your strand that fills it |
|---|---|---|
| Flexible point estimates (composite-likelihood NMA, class-effects, vine-copula DTA) | Whether the result **agrees with itself** (consistency of inputs, ranks, contributions) | **Self-auditing / TruthCert** |
| Nominal CIs / CrIs (sandwich, MCMC) | **Honest interval coverage at small k** (sandwich under-covers; CINeMA imprecision is qualitative) | **Conformal / PI honest-coverage** |
| One "preferred model" (model-selection algorithms, RoBMA averaging) | Robustness to the **analyst's forking-path choices** as a first-class output | **Spec-collapse / multiverse** |

> **The synthesis is not a new estimator.** It is a *standardised assurance + honest-coverage + multiverse-robustness wrapper* that any frontier complex-evidence estimator plugs into, producing a signed capsule whose ranks/effects come with (a) a self-consistency verdict, (b) a calibrated interval that does not over-claim at small k, and (c) a specification-curve showing how fragile the conclusion is to defensible analyst choices.

This is publishable as a **methods + standard** contribution (the wrapper), demonstrable as **capsules** (the engines), and it is differentiated: no frontier paper below ships all three layers, and CINeMA/GRADE deliver the assurance layer only qualitatively.

---

## 2. Frontier method catalog (NMA / DTA / complex evidence, 2024–2026)

### NMA
| # | Method | Source | What's new | Maturity |
|---|---|---|---|---|
| N1 | **Composite-likelihood NMA + sandwich robust variance** | RSM 2024 (PMC11213057; PubMed 38947001; medRxiv 2024.06.19.24309163) | Valid inference **without within-study correlations**; scales to large networks. **Caveat: sandwich under-covers at small k (CI coverage 88–94%).** | Published, R available |
| N2 | **Calibrated Bayesian composite-likelihood multivariate NMA** | PMC11230323; PubMed 38978647 | Open-Faced Sandwich post-sampling adjustment; hybrid Gibbs; multi-outcome without full likelihood | Published |
| N3 | **Class-effects NMA + model-selection algorithm** | Perren, Pedder, Welton, Phillippo, *Med Decis Making* 2026 (10.1177/0272989X251389887) | Practical guide + algorithm for when to pool drugs into classes | Published 2026 |
| N4 | **Threshold analysis for NMA recommendations** | Phillippo et al; application PMC9107143 | Quantifies how much bias a recommendation can absorb before the decision flips | Mature, under-used |
| N5 | **CINeMA confidence framework + contribution-matrix automation** | PLOS Med 2020 (pmed.1003082); concordance study Minozzi 2025 (S0895435625001441) | Semi-automated GRADE-for-NMA; 6 domains; *2025 finding: efficient but less transparent than GRADE* | Mature + active research |
| N6 | **PRISMA-NMA reporting update** | Scoping review S089543562500318X; Delphi early 2026 | Reporting standard refresh (transitivity/consistency) | In progress |
| N7 | **Multiplicative-heterogeneity NMA** | (allmeta already implements; arXiv:2601.11735 in stats rules) | Alternative to additive RE under small-study effects | Published |

### DTA
| # | Method | Source | What's new | Maturity |
|---|---|---|---|---|
| D1 | **Multiple-threshold DTA (pseudo-likelihood, working-independence)** | arXiv:1804.08665; data-integration PubMed 36228672 | No within-study correlations; avoids convergence failure across thresholds | Published |
| D2 | **Vine-copula random-effects DTA** | (copula DTA line; meta4diag context arXiv:1512.06220) | Reflection-asymmetric tail dependence; richer than trivariate GLMM | Published |
| D3 | **NMA of DTA (rank competing tests/thresholds)** | PubMed 29548843 | Identifies optimal test+threshold across a network | Published |
| D4 | **DTA with multiple disease stages (merged + stage-specific)** | Derezea, Welton, Rogers, Jones 2026, arXiv:2512.12065 | Combines studies reporting merged-stage vs stage-specific sensitivity | **New (Feb 2026)** |

### Cross-cutting (robustness / coverage / averaging)
| # | Method | Source | What's new | Maturity |
|---|---|---|---|---|
| X1 | **Robust Bayesian MA model-averaging (RoBMA)** | Bartoš et al 2023 RSM (jrsm.1594); Maier/Bartoš/Wagenmakers 2022 (PubMed 35588075); RoBMA pkg Dec 2025 | Averages across pub-bias adjustment methods weighted by marginal likelihood | Mature, R pkg |
| X2 | **New selection model** | Pustejovsky, Citkowicz & Joshi 2025 | Selection model robust to step-function misspecification | Published 2025 |
| X3 | **Robust Bayesian multilevel MA (dependent effects)** | s13428-026-03023-y (2026) | Pub-bias adjustment under dependent effect sizes | New 2026 |
| X4 | **Single-dataset many-analysts / multiverse MA** | arXiv:2511.17064 | **Naive IV-RE pooling of multiverse specs collapses CIs below truth** — use weighted-likelihood | New, in your stats rules |
| X5 | **Conformal frontier** | extreme arXiv:2505.08578; online-efficiency 2507.02496; weighted-Bayesian 2604.06464; functional-TS 2605.29296; federated-MA 2604.23847 | Finite-sample marginal coverage; nonexchangeable / weighted variants | Very active 2025–26 |

---

## 3. Honesty constraints carried in from your own findings

These are *guardrails*, not options — they are where your prior work already disproved the naive frontier story:

- **C1 — Conformal does NOT free-lunch small-k coverage.** `conformal-ma` honest out-of-sample eval (LOO + known-truth sim, metafor-validated) showed **standard PI beats conformal at small k; conformal under-covers.** Any conformal layer must be benchmarked out-of-sample, never claimed in-sample. (memory: `conformal-ma-honest-refutation`)
- **C2 — Never IV-RE-pool multiverse specs.** arXiv:2511.17064 + your `spec-collapse-atlas` weighted-likelihood aggregator. The multiverse layer is **descriptive heterogeneity + weighted-likelihood**, not a second random-effects pool.
- **C3 — Sandwich/composite-likelihood under-covers at small k** (N1, 88–94%). The honest-coverage layer (conformal *or* HKSJ-style small-sample correction) is what earns back nominal coverage — this is the *natural seam* where your PI work meets the frontier estimator.
- **C4 — Multiplicative-NMA / additive-RE choice is itself a forking path** → belongs in the multiverse layer, not hard-coded (stats rules: AIC-favours-by-≥2 switch rule).
- **C5 — SUCRA needs POTH; rank claims need rank-uncertainty.** Self-auditing layer must gate "X ranked best" on POTH ≥ 0.5 (stats rules).

---

## 4. Fusion matrix — *what to integrate where*

Reading: **frontier method (rows) × your strand (cols)**. Cell = the concrete fused artifact. `[reuse]` / `[net-new]` flags the build.

### Strand A — Self-auditing / TruthCert
- **N1/N2 composite-likelihood NMA** → self-consistency checks: design-by-treatment + node-split run automatically; contribution-matrix sanity; sign/scale agreement of robust vs model-based SE. `[reuse allmeta/nma-inconsistency, nma-global-inconsistency]` + `[net-new TruthCert verdict block]`
- **N5 CINeMA** → encode the 6 CINeMA domains as **machine-checkable internal-consistency rules** (your assurance standard's whole premise: "the capsule agrees with itself before asking the world to"). This is the single biggest differentiator vs CINeMA's qualitative ratings. `[net-new]` over `[reuse e156-assurance-standard, grade-capsule.html]`
- **D3/D4 DTA-NMA & disease-stages** → auto-check threshold monotonicity, stage-proportion closure (merged = Σ stage-specific). `[net-new]`

### Strand B — Conformal / PI honest-coverage
- **N1 sandwich under-coverage (C3)** → wrap the composite-likelihood NMA in a **split-conformal / calibrated PI layer**, benchmarked out-of-sample per C1. This is the headline fusion: *frontier estimator's scalability + your honest-coverage rescue of its known small-k under-coverage.* `[reuse conformal-ma pipeline]` + `[net-new NMA adapter]`
- **D1/D2 DTA** → calibrated joint (Se,Sp) prediction region using bivariate-conformal; compare vs your existing `sqrt(chi2_{alpha,2})` region (stats rules). `[reuse dta-sroc, truth-recovery-bench DTA]`
- **X5 weighted/online conformal** → for `denominator-calibrated-living-nma` (a *living* NMA), online conformal with efficiency guarantees (2507.02496) gives valid sequential PIs as trials accrue. `[net-new]` strong fit.

### Strand C — Spec-collapse / multiverse
- **N3 class-effects + N7 multiplicative-vs-additive (C4)** → these *are* forking paths: enumerate {class structure, additive/multiplicative τ², reference treatment, tie-handling} as the NMA multiverse grid; aggregate with **weighted-likelihood per C2**, emit a specification curve over treatment ranks. `[reuse spec-collapse-atlas aggregator, fragility-atlas]` + `[net-new NMA spec-grid]`
- **X1/X2/X3 RoBMA** → model-averaging *is* a principled multiverse over pub-bias models; fold RoBMA's marginal-likelihood weights into your weighted-likelihood aggregator so pub-bias adjustment becomes one axis of the spec-curve rather than a separate analysis. `[net-new bridge]`
- **D4 merged/stage-specific DTA** → the "which studies to include (merged vs stage-specific)" decision is a forking path → multiverse axis. `[net-new]`

---

## 5. Prioritised roadmap (leverage × effort)

| Pri | Integration | Strand × method | Leverage | Effort | Home repo |
|---|---|---|---|---|---|
| **P0** | Conformal/calibrated-PI wrapper on composite-likelihood NMA, out-of-sample benchmarked | B × N1 | **High** — fixes a *published* coverage weakness; clean methods-paper claim | M | new module in `allmeta/nma` + `conformal-ma` |
| **P0** | CINeMA-6-domains → machine-checkable self-audit verdict | A × N5 | **High** — turns qualitative confidence into signed, reproducible check; unique | M | `e156` assurance + `grade-capsule.html` |
| **P1** | NMA specification-grid + weighted-likelihood aggregation (class/τ²-form/reference) | C × N3/N7 | **High** — ranks-fragility is decision-relevant & under-served | M–L | `spec-collapse-atlas` + `allmeta` |
| **P1** | RoBMA-weights → multiverse axis bridge | C × X1 | Med | M | `spec-collapse-atlas` |
| **P2** | Online conformal PIs for living NMA | B × X5 | Med | M | `denominator-calibrated-living-nma` |
| **P2** | Disease-stage DTA (D4) + monotonicity/closure self-audit + conformal region | A/B × D4 | Med (new, narrow) | M | `dta-sroc` / `dta-floor-atlas` |
| **P2** | Threshold-analysis (N4) as a self-audit "decision-flip" robustness witness | A × N4 | Med | S–M | `allmeta/nma` |

**Recommended Phase 1 (one milestone, ship before expanding):** the two **P0** items on a single worked NMA dataset already in the portfolio (e.g. an `aact-cockpit` NMA capsule), producing one signed capsule that demonstrates *frontier estimator → self-audit verdict → honest PI*. That is the minimum that proves the synthesis and is itself an E156-publishable unit.

---

## 6. Risks / what would kill this

- **Coverage claim must survive out-of-sample (C1).** If the conformal wrapper under-covers like `conformal-ma` found, the P0-B headline weakens — mitigate by also shipping the HKSJ/small-sample correction as the honest fallback and *reporting whichever wins*, per your repro-floor discipline.
- **Multiverse CI collapse (C2).** Aggregation must be weighted-likelihood, never IV-RE — already solved in `spec-collapse-atlas`; the risk is a re-implementation drifting from it. Reuse, don't re-derive.
- **CINeMA-as-rules over-claiming.** Encoding 6 qualitative domains as binary checks can look more certain than CINeMA intends — keep domain outputs graded (Bronze/Silver/Gold per assurance standard), not pass/fail.
- **Scope creep.** Seven integrations listed; commit to the two P0 first with a checkpoint (workflow rule).

## 7. Sources

- Composite-likelihood NMA — https://pmc.ncbi.nlm.nih.gov/articles/PMC11213057/ , https://pubmed.ncbi.nlm.nih.gov/38947001/ , https://www.medrxiv.org/content/10.1101/2024.06.19.24309163v1.full
- Calibrated Bayesian composite-likelihood multivariate NMA — https://pmc.ncbi.nlm.nih.gov/articles/PMC11230323/ , https://pubmed.ncbi.nlm.nih.gov/38978647/
- Class-effects NMA + model selection — https://journals.sagepub.com/doi/10.1177/0272989X251389887
- Twenty years of NMA (review) — https://onlinelibrary.wiley.com/doi/full/10.1002/jrsm.1700
- Threshold analysis (application) — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9107143/
- CINeMA — https://journals.plos.org/plosmedicine/article?id=10.1371%2Fjournal.pmed.1003082 ; GRADE-vs-CINeMA concordance 2025 — https://www.sciencedirect.com/science/article/abs/pii/S0895435625001441
- PRISMA-NMA update scoping review — https://www.sciencedirect.com/science/article/pii/S089543562500318X
- DTA multiple thresholds — https://arxiv.org/pdf/1804.08665 ; https://pubmed.ncbi.nlm.nih.gov/36228672/
- DTA disease stages (2026) — https://arxiv.org/abs/2512.12065
- NMA of DTA — https://pubmed.ncbi.nlm.nih.gov/29548843/
- RoBMA model-averaging — https://onlinelibrary.wiley.com/doi/full/10.1002/jrsm.1594 ; https://pubmed.ncbi.nlm.nih.gov/35588075/ ; https://cran.r-project.org/web/packages/RoBMA/RoBMA.pdf
- Robust Bayesian multilevel (dependent effects, 2026) — https://link.springer.com/article/10.3758/s13428-026-03023-y
- Single-dataset many-analysts MA — https://arxiv.org/pdf/2511.17064
- Conformal frontier — https://arxiv.org/abs/2505.08578 , https://arxiv.org/abs/2507.02496 , https://arxiv.org/html/2604.06464 , https://arxiv.org/abs/2605.29296
