"""Assemble the combined Phase-1 verdict: honest PI coverage (P0-B) + CINeMA-6
self-audit (P0-A) into one capsule-ready, signing-ready block.

This is the artifact the published capsule would carry: the frontier estimator's
effect, an honestly-selected prediction interval, and a machine-checkable
certainty badge -- the three-layer "verifiable complex-evidence synthesis".
"""

from __future__ import annotations

import json
from pathlib import Path

from phase1 import coverage, data_io, selfaudit


def assemble(net: dict) -> dict:
    rep = coverage.report(net)
    rec_name = rep["recommendation"]["recommended"]
    rec_pi = rep["intervals"]["intervals"].get(rec_name)
    audit = selfaudit.cinema6_verdict(net, rec_pi)

    return {
        "dataset": net["slug"],
        "estimand": net.get("primary_estimand"),
        "k": rep["k"],
        "effect_logHR_active_vs_placebo": round(rep["theta"], 6),
        "tau2": round(rep["tau2"], 6),
        "prediction_interval": {
            "method": rec_name,
            "meets_nominal": rep["recommendation"]["meets_nominal"],
            "logHR": [round(rec_pi[0], 6), round(rec_pi[1], 6)],
        },
        "loo_coverage": {m: (round(c, 4) if c == c else None)
                         for m, c in rep["loo_coverage"].items()},
        "known_truth_coverage": {m: round(s["coverage"], 4)
                                 for m, s in rep["known_truth_sim"]["by_method"].items()},
        "cinema6_levels": {k: d["level"] for k, d in audit["cinema6"].items()},
        "certainty": audit["grade"]["certainty"],
        "badge": audit["grade"]["badge"],
    }


def main() -> int:
    net = data_io.load_network()
    v = assemble(net)
    out_dir = Path(__file__).resolve().parent / "output"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "verdict.json").write_text(json.dumps(v, indent=2), encoding="utf-8")
    print(json.dumps(v, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
