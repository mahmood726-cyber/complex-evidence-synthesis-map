"""B2: core_ad NMA wiring + sandwich-variance option.

Validates the pseudo-arm reconstruction (effects match the independent aact NMA
engine), the point-estimate invariance to the variance choice, and the documented
small-cluster sandwich behaviour."""

import math

import pytest

from phase1 import data_io
from phase2 import core_nma


@pytest.fixture(scope="module")
def net():
    return data_io.load_network()


def test_dataset_shape(net):
    ds = core_nma.build_dataset(net)
    assert len(ds.studies) == 10
    assert len(ds.arms) == 20          # 2 pseudo-arms per contrast
    assert len(ds.outcomes_ad) == 20


def test_effects_match_aact_engine(net):
    # core_ad NMA (shared-tau REML) must reproduce the independent aact engine's
    # network effects -> corroborates the pseudo-arm reconstruction.
    fm = core_nma.fit(net, "model")
    for t in fm.parameter_treatments:
        d = abs(fm.treatment_effects[t] - net["nma"]["effects"][t])
        assert d < 1e-3, f"{t}: core_ad {fm.treatment_effects[t]} vs aact {net['nma']['effects'][t]}"


def test_point_estimates_invariant_to_variance(net):
    fm = core_nma.fit(net, "model")
    fs = core_nma.fit(net, "sandwich")
    assert abs(fm.tau - fs.tau) < 1e-12
    for t in fm.parameter_treatments:
        assert fm.treatment_effects[t] == pytest.approx(fs.treatment_effects[t], abs=1e-12)


def test_sandwich_changes_se(net):
    rep = core_nma.compare(net)
    # at least one treatment's sandwich SE differs from the model SE
    assert any(abs(d["se_sandwich"] - d["se_model"]) > 1e-4
               for d in rep["by_treatment"].values())
    # all SEs finite and non-negative
    for d in rep["by_treatment"].values():
        assert d["se_model"] >= 0 and d["se_sandwich"] >= 0
        assert math.isfinite(d["se_sandwich"])


def test_small_cluster_sandwich_unreliable(net):
    # DPP-4 is informed by only 2 studies; the cluster-robust sandwich is known
    # to collapse/under-cover at tiny cluster counts (the N1 caveat). Assert it
    # under-shoots the model SE there rather than silently trusting it.
    rep = core_nma.compare(net)
    dpp = rep["by_treatment"]["DPP-4 inhibitor"]
    assert dpp["se_sandwich"] < dpp["se_model"]
