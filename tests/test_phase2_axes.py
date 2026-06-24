"""Phase-2 extension axes: multiplicative-NMA (C4) and RoBMA-style pub-bias."""

import pytest

from phase1 import data_io
from phase2 import multiverse, pubbias, specs


@pytest.fixture(scope="module")
def net():
    return data_io.load_network()


def _contrast(net, t):
    s = data_io.studies_for_treatment(net, t)
    return [x.yi for x in s], [x.sei ** 2 for x in s]


# ---- multiplicative-NMA axis (C4) ------------------------------------------

def test_multiplicative_phi_at_least_one(net):
    for t in data_io.active_treatments(net):
        yi, vi = _contrast(net, t)
        m = specs.pool_multiplicative(yi, vi)
        assert m["phi"] >= 1.0                       # floored overdispersion
        assert m["het_model"] == "multiplicative"


def test_multiplicative_point_estimate_is_fixed_effect(net):
    # multiplicative theta == fixed-effect mean (only the variance is scaled)
    yi, vi = _contrast(net, "SGLT2 inhibitor")
    m = specs.pool_multiplicative(yi, vi)
    fe = specs.pool_one(yi, vi, "FE", "Wald")
    assert m["theta"] == pytest.approx(fe["theta"], abs=1e-9)


def test_c4_switch_rule(net):
    for t in data_io.active_treatments(net):
        yi, vi = _contrast(net, t)
        c = specs.multiplicative_vs_additive(yi, vi)
        assert c["choice"] in ("additive", "multiplicative", "indistinguishable")
        # C4: only switch when |dAIC| >= 2
        if c["choice"] == "indistinguishable":
            assert abs(c["delta_aic_add_minus_mult"]) < 2


# ---- RoBMA-style publication-bias axis -------------------------------------

def test_robma_weights_sum_to_one(net):
    yi, vi = data_io.active_vs_placebo_sample(net)
    vi = [s ** 2 for s in vi]
    pb = pubbias.robma_style(yi, vi)
    w = sum(m["weight"] for m in pb["models"])
    assert w == pytest.approx(1.0, abs=1e-6)
    assert {m["method"] for m in pb["models"]} == {"raw", "trim_fill", "pet_peese"}


def test_robma_underpowered_flag():
    # k < 10 must be flagged underpowered (honest small-k guard)
    pb = pubbias.robma_style([0.1, -0.2, 0.05], [0.04, 0.05, 0.03])
    assert pb["underpowered"] is True


def test_robma_model_averaged_not_narrower_than_significance_flip(net):
    # on this network the pub-bias-averaged effect stays non-significant (the
    # adjustment does not manufacture a signal)
    yi, vi = data_io.active_vs_placebo_sample(net)
    vi = [s ** 2 for s in vi]
    pb = pubbias.robma_style(yi, vi)
    assert pb["model_averaged"]["significant"] is False


def test_pet_peese_small_k_falls_back_to_raw():
    s = pubbias.spec_pet_peese([0.1, 0.2], [0.04, 0.05])  # k=2
    assert "fell back to raw" in s.get("note", "")
