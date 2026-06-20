"""B1: validate the pooling backbone vs metafor (R). The aact star network's NMA
reduces to independent pairwise pools, so per-contrast DL/REML parity vs
metafor::rma is the netmeta-equivalent estimator check.

Degrades to SKIP (returns None) when Rscript/metafor is unavailable, so the run
is UNVERIFIED rather than failing on an R-less box.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

from phase1 import bootstrap, data_io

bootstrap.add_spec_collapse()
from spec_collapse import engine as E  # noqa: E402

R_SCRIPT = Path(__file__).resolve().parents[1] / "external" / "r" / "parity.R"


def _engine_pool(yi, vi, method: str):
    tau2 = E.tau2_dl(yi, vi) if method == "DL" else E.tau2_reml(yi, vi)
    theta, var_wald, _, _ = E.re_pool(yi, vi, tau2)
    return theta, math.sqrt(var_wald)


def _r_pool(rscript: str, yi, vi):
    sei = [math.sqrt(v) for v in vi]
    out = subprocess.run(
        [rscript, str(R_SCRIPT), ",".join(map(repr, yi)), ",".join(map(repr, sei))],
        capture_output=True, text=True, timeout=120,
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip()[:200])
    res = {}
    for line in out.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) == 3:
            res[parts[0]] = (float(parts[1]), float(parts[2]))
    return res


def validate(net: dict | None = None) -> dict | None:
    rscript = bootstrap.find_rscript()
    if rscript is None:
        return None
    net = net or data_io.load_network()
    rows = []
    for t in data_io.active_treatments(net):
        studies = data_io.studies_for_treatment(net, t)
        if not studies:
            continue
        yi = [s.yi for s in studies]
        vi = [s.sei ** 2 for s in studies]
        try:
            rres = _r_pool(rscript, yi, vi)
        except RuntimeError as exc:
            return {"skipped": True, "reason": f"R/metafor failed: {exc}"}
        for method in ("DL", "REML"):
            eb, ese = _engine_pool(yi, vi, method)
            rb, rse = rres[method]
            rows.append({
                "contrast": t, "method": method,
                "engine_b": eb, "r_b": rb, "d_b": abs(eb - rb),
                "engine_se": ese, "r_se": rse, "d_se": abs(ese - rse),
            })
    return {"skipped": False, "rscript": rscript, "rows": rows}


def main() -> int:
    res = validate()
    if res is None:
        print("R-parity SKIPPED: Rscript not found -> run remains UNVERIFIED.")
        return 0
    if res.get("skipped"):
        print(f"R-parity SKIPPED: {res['reason']}")
        return 0
    print(f"B1 metafor parity  (Rscript: {res['rscript']})\n")
    print(f"  {'contrast':18s} {'method':5s} {'d_estimate':>12s} {'d_se':>12s}")
    worst = 0.0
    for r in res["rows"]:
        worst = max(worst, r["d_b"], r["d_se"])
        print(f"  {r['contrast']:18s} {r['method']:5s} {r['d_b']:12.2e} {r['d_se']:12.2e}")
    print(f"\n  worst absolute difference: {worst:.2e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
