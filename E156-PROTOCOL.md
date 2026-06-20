# E156 Protocol — Verifiable Complex-Evidence Synthesis (NMA worked example)

- **Project:** complex-evidence-synthesis-map
- **Repo:** https://github.com/mahmood726-cyber/complex-evidence-synthesis-map
- **Phase 0 (map):** 2026-06-20 · **Phase 1–2 (implementation):** 2026-06-20
- **Primary estimand:** the number of active-vs-placebo contrasts whose effect remains statistically robust under *correct* (weighted-likelihood) multiverse aggregation.
- **Dataset:** aact NMA-MACE-in-T2D, 10-study star network (DPP-4i, GLP-1 RA, SGLT2i vs placebo), ClinicalTrials.gov via AACT.
- **Verification:** estimator matches `metafor` to 7e-07 (R 4.6.0); 29 tests green; seeded MC; version-controlled numerical baselines.
- **Reuses:** `conformal-ma` (PI primitives), `spec-collapse-atlas` (`weighted_likelihood`, pooling engine), `advanced-nma-pooling`, e156 assurance standard.

## Body (7 sentences, 155 words)

Does a significant cardiovascular-safety network meta-analysis across three diabetes drug classes survive a verifiability-first re-analysis adding self-audit, honest coverage, and a multiverse? We re-analysed a ten-study network comparing DPP-4 inhibitors, GLP-1 agonists, and SGLT2 inhibitors versus placebo for cardiovascular events, via AACT. Each contrast was pooled under eight specifications (fixed-effect, DerSimonian-Laird, Paule-Mandel, REML, with Wald or HKSJ intervals) and aggregated by weighted-likelihood. The primary estimand, the number of contrasts statistically robust under correct aggregation, was zero of three, whereas inverse-variance pooling labelled two of three robust by narrowing intervals roughly sixfold. Leave-one-out prediction intervals covered ninety percent versus a nominal ninety-five, and the treatment-hierarchy probability POTH was 0.21, below the 0.5 informativeness threshold. The headline cardiovascular signal and apparent best-drug ranking are artefacts of analytic choices and rank uncertainty that verifiability-first synthesis exposes and reverses. This demonstrates the method on one small network with unassessed risk-of-bias and reporting domains, so larger, loop-containing networks remain untested.

## Authorship (per workbook rule)

MA is middle-author only (role: software, methodology, supervision-of-tooling) — never first or senior author. Student rewriter is first author; senior author is a faculty supervisor distinct from MA.
