"""Task 0 — prereq preflight. Fails closed; SKIPs external tools with a reason.

Run:  python -m phase1.preflight
Exit codes: 0 = PASS or UNVERIFIED (runnable), 1 = FAIL (blocker).

A blocker (exit 1) is any of: vendored data missing/corrupt. Missing sibling
repos or R/netmeta downgrade the run to UNVERIFIED but do not block, mirroring
the verdict-schema rule that a SKIP is not a silent PASS.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

from phase1 import bootstrap, data_io


def _check(name: str, fn):
    try:
        ok, detail = fn()
        return {"check": name, "status": "pass" if ok else "skip", "detail": detail}
    except Exception as exc:  # noqa: BLE001 - report any failure as a blocker
        return {"check": name, "status": "fail", "detail": f"{type(exc).__name__}: {exc}"}


def check_dataset():
    net = data_io.load_network()
    rows = data_io.contrasts(net)  # raises on any invalid yi/sei (fail closed)
    k = len(rows)
    if k < 2:
        return False, f"only {k} contrasts"
    seis = [r.sei for r in rows]
    return True, (
        f"k={k} studies, reference={data_io.reference(net)!r}, "
        f"sei in [{min(seis):.4f}, {max(seis):.4f}], all finite & > 0"
    )


def check_advanced_nma_pooling():
    repo = bootstrap.add_advanced_nma_pooling()
    if repo is None:
        return False, "advanced-nma-pooling not found (set ADVANCED_NMA_POOLING_DIR) -> estimator-parity SKIP"
    from nma_pool.models.core_ad import NMAFitResult  # noqa: F401
    from nma_pool.data.builder import EvidenceDataset  # noqa: F401
    return True, f"importable from {repo}"


def check_conformal_ma():
    repo = bootstrap.add_conformal_ma()
    if repo is None:
        return False, "conformal-ma not found (set CONFORMAL_MA_DIR) -> conformal layer SKIP"
    import pipeline  # noqa: F401
    fns = ["conformal_prediction_set", "standard_prediction_interval",
           "hksj_prediction_interval", "heldout_interval_coverage"]
    missing = [f for f in fns if not hasattr(pipeline, f)]
    if missing:
        return False, f"conformal-ma present but missing {missing}"
    return True, f"PI primitives importable from {repo}"


def check_r_netmeta():
    if shutil.which("Rscript") is None:
        return False, "Rscript not on PATH -> netmeta parity SKIP (run is UNVERIFIED, validate via known-truth)"
    try:
        r = subprocess.run(
            ["Rscript", "-e", "suppressMessages(library(netmeta)); cat('ok')"],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"Rscript present but failed: {exc}"
    if "ok" in (r.stdout or ""):
        return True, "Rscript + netmeta available"
    return False, f"netmeta not installed: {(r.stderr or '').strip()[:120]} -> parity SKIP"


def run() -> dict:
    results = [
        _check("vendored_dataset", check_dataset),
        _check("advanced_nma_pooling", check_advanced_nma_pooling),
        _check("conformal_ma", check_conformal_ma),
        _check("r_netmeta", check_r_netmeta),
    ]
    blockers = [r for r in results if r["status"] == "fail"]
    skips = [r for r in results if r["status"] == "skip"]
    if blockers:
        verdict = "FAIL"
    elif skips:
        verdict = "UNVERIFIED"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "results": results}


def main() -> int:
    report = run()
    print(f"PHASE-1 PREFLIGHT: {report['verdict']}\n")
    for r in report["results"]:
        mark = {"pass": "[OK]  ", "skip": "[SKIP]", "fail": "[FAIL]"}[r["status"]]
        print(f"  {mark} {r['check']}: {r['detail']}")
    if report["verdict"] == "FAIL":
        print("\nBLOCKER(S) present -- resolve the [FAIL] items above before proceeding.")
        return 1
    if report["verdict"] == "UNVERIFIED":
        print("\nRunnable, but external validators are SKIPPED -> results are UNVERIFIED, not a release PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
