"""Numerical-baseline regression: the assembled verdict must match the
version-controlled fixture within tolerance (deterministic: seeded sim + closed-
form PIs). Guards against silent drift in any reused primitive."""

import json
from pathlib import Path

import pytest

from phase1 import data_io, verdict

FIXTURE = Path(__file__).parent / "fixtures" / "verdict_baseline.json"


@pytest.fixture(scope="module")
def baseline():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_verdict_matches_baseline(baseline):
    v = verdict.assemble(data_io.load_network())

    assert v["k"] == baseline["k"]
    assert v["effect_logHR_active_vs_placebo"] == pytest.approx(
        baseline["effect_logHR_active_vs_placebo"], abs=1e-6)
    assert v["tau2"] == pytest.approx(baseline["tau2"], abs=1e-6)

    assert v["prediction_interval"]["method"] == baseline["prediction_interval"]["method"]
    assert v["prediction_interval"]["logHR"] == pytest.approx(
        baseline["prediction_interval"]["logHR"], abs=1e-6)

    for m in ("conformal", "standard", "hksj"):
        assert v["loo_coverage"][m] == pytest.approx(baseline["loo_coverage"][m], abs=1e-6)
        assert v["known_truth_coverage"][m] == pytest.approx(
            baseline["known_truth_coverage"][m], abs=1e-6)

    assert v["cinema6_levels"] == baseline["cinema6_levels"]
    assert v["badge"] == baseline["badge"]
    assert v["certainty"] == baseline["certainty"]
