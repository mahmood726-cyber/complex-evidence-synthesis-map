"""Disease-stage DTA axis (D4): known-truth recovery, the include-merged
forking-path, and the stage-closure / monotonicity self-audit."""

import pytest

from phase2 import dta_stages as D


def test_recovers_true_stage_sensitivities():
    fit = D.fit(D.make_data(se_early=0.60, se_late=0.90), include_merged=True)
    assert fit["se_stage"][0] == pytest.approx(0.60, abs=0.05)
    assert fit["se_stage"][1] == pytest.approx(0.90, abs=0.05)


def test_adding_merged_sharpens_estimates():
    rep = D.inclusion_axis(D.make_data())
    assert rep["with_merged"]["n_used"] > rep["stage_specific_only"]["n_used"]
    assert rep["se_narrowed"] == [True, True]   # both stage SEs narrow with merged data


def test_stage_closure_self_audit():
    studies = D.make_data()
    rep = D.inclusion_axis(studies)
    assert rep["closure"]["passes"] is True
    assert rep["closure"]["n_merged"] == 4


def test_stage_monotonicity_self_audit():
    rep = D.inclusion_axis(D.make_data(se_early=0.60, se_late=0.90))
    assert rep["monotonicity"]["monotone"] is True


def test_merged_only_is_under_identified():
    merged = [{"type": "merged", "props": [0.5, 0.5], "se_obs": 0.75, "var": 0.0016}
              for _ in range(3)]
    with pytest.raises(ValueError):
        D.fit(merged, include_merged=True)
