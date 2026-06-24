"""RoBMA-in-R cross-check for the portable pub-bias model-averaging (phase2.pubbias).

RoBMA requires JAGS (>=4.3.1), an external Windows runtime. When JAGS/RoBMA are
unavailable the cross-check SKIPS with a reason (the run stays UNVERIFIED for this
component, like the B1 R-skip) -- never a silent pass. When present, it compares
the RoBMA model-averaged mu to phase2.pubbias.robma_style.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

from phase1 import bootstrap, data_io
from phase2 import pubbias

R_SCRIPT = Path(__file__).resolve().parents[1] / "external" / "r" / "robma.R"


def jags_available() -> bool:
    """JAGS installs to C:\\Program Files\\JAGS on Windows; required by RoBMA's DLL."""
    base = Path(r"C:\Program Files\JAGS")
    return base.exists() and any(base.glob("JAGS-*"))


def validate(net: dict | None = None) -> dict | None:
    rscript = bootstrap.find_rscript()
    if rscript is None:
        return {"skipped": True, "reason": "Rscript not found"}
    if not jags_available():
        return {"skipped": True,
                "reason": "JAGS not installed (C:\\Program Files\\JAGS); RoBMA native DLL "
                          "cannot load. Install JAGS>=4.3.1, then reinstall RoBMA."}
    net = net or data_io.load_network()
    yi, sei = data_io.active_vs_placebo_sample(net)
    vi = [s ** 2 for s in sei]
    out = subprocess.run([rscript, str(R_SCRIPT), ",".join(map(repr, yi)),
                          ",".join(map(repr, sei))],
                         capture_output=True, text=True, timeout=600)
    line = (out.stdout or "").strip().splitlines()[-1] if out.stdout else ""
    if line.startswith("ROBMA_UNAVAILABLE"):
        return {"skipped": True, "reason": line}
    parts = line.split()
    if len(parts) != 4 or parts[0] != "ROBMA":
        return {"skipped": True, "reason": f"unparsable RoBMA output: {line[:120]}"}
    robma_mu = float(parts[1])
    portable = pubbias.robma_style(yi, vi)["model_averaged"]["theta"]
    return {"skipped": False, "robma_mu": robma_mu, "portable_mu": portable,
            "abs_diff": abs(robma_mu - portable)}


def main() -> int:
    res = validate()
    if res.get("skipped"):
        print(f"RoBMA cross-check SKIPPED: {res['reason']}")
        print("-> portable RoBMA-style model-averaging (phase2.pubbias) remains the implementation.")
        return 0
    print(f"RoBMA mu={res['robma_mu']:+.4f}  portable mu={res['portable_mu']:+.4f}  "
          f"|diff|={res['abs_diff']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
