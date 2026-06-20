"""Load the vendored aact NMA-MACE-in-T2D network (standalone, no user-home).

The network is a star design (every active class vs placebo). Each contrast row
is one study with a log-effect `yi` and standard error `sei` on the reference
treatment. We expose:
  - the full study-level contrast table
  - per-active-treatment study lists (the studies informing that vs-reference effect)
  - the pre-computed pooled fit summary (effects, tau2, Q, df, k, consistency)
    that the aact engine produced, used as an independent parity anchor.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "nma_mace_t2d.json"


@dataclass(frozen=True)
class Contrast:
    nct: str
    study: str
    t1: str
    t2: str
    yi: float
    sei: float


class DataError(ValueError):
    """Raised on a data-integrity violation (fail closed, never impute)."""


def load_network(path: Path | None = None) -> dict:
    p = path or DATA_PATH
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def contrasts(net: dict) -> list[Contrast]:
    rows: list[Contrast] = []
    for c in net["contrasts"]:
        yi = c.get("yi")
        sei = c.get("sei")
        nct = c.get("nct", "?")
        if yi is None or not math.isfinite(yi):
            raise DataError(f"contrast {nct}: non-finite yi={yi!r}")
        if sei is None or not math.isfinite(sei) or sei <= 0:
            # fail closed: a zero/missing SE breaks every PI; do not impute.
            raise DataError(f"contrast {nct}: invalid sei={sei!r} (must be > 0)")
        rows.append(Contrast(nct, c.get("study", ""), c["t1"], c["t2"], float(yi), float(sei)))
    return rows


def reference(net: dict) -> str:
    return net["reference"]


def studies_for_treatment(net: dict, treatment: str) -> list[Contrast]:
    """Studies that directly compare `treatment` against the reference.

    The star network orients some rows as placebo-vs-active and others as
    active-vs-placebo; we normalise the sign so every returned yi is the effect
    of `treatment` relative to the reference treatment.
    """
    ref = reference(net)
    out: list[Contrast] = []
    for c in contrasts(net):
        if treatment in (c.t1, c.t2) and ref in (c.t1, c.t2) and treatment != ref:
            if c.t1 == treatment and c.t2 == ref:
                out.append(c)
            elif c.t1 == ref and c.t2 == treatment:
                # row is ref-vs-treatment -> flip sign to treatment-vs-ref
                out.append(Contrast(c.nct, c.study, treatment, ref, -c.yi, c.sei))
    return out


def active_treatments(net: dict) -> list[str]:
    ref = reference(net)
    return [t for t in net["treatments"] if t != ref]


def pooled_summary(net: dict) -> dict:
    """The aact engine's own pooled NMA result (independent parity anchor)."""
    return net["nma"]


def active_vs_placebo_sample(net: dict) -> tuple[list[float], list[float]]:
    """All studies oriented as active-minus-reference (class-pooled).

    NOTE: pooling distinct drug classes into one 'active vs placebo' effect
    assumes class exchangeability -- a debatable analyst choice that is itself a
    multiverse axis (Phase-2 P1). Used here only to obtain a k=10 effect sample
    in the small-k regime where conformal coverage is the open question.
    """
    ref = reference(net)
    yi: list[float] = []
    sei: list[float] = []
    for c in contrasts(net):
        if ref not in (c.t1, c.t2):
            continue
        if c.t1 == ref:  # ref-vs-active -> flip to active-vs-ref
            yi.append(-c.yi)
        else:  # active-vs-ref
            yi.append(c.yi)
        sei.append(c.sei)
    return yi, sei
