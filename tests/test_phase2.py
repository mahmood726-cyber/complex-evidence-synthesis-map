"""Phase-2 multiverse tests: spec grid, SUCRA/POTH, and the C2 cardinal-sin gap."""

import pytest

from phase1 import data_io
from phase2 import multiverse, ranking, specs


@pytest.fixture(scope="module")
def net():
    return data_io.load_network()


@pytest.fixture(scope="module")
def rep(net):
    return multiverse.report(net, n_mc=20000, seed=20260620)


# ---- spec grid -------------------------------------------------------------

def test_grid_size_and_fe_zero_tau2(net):
    t = "SGLT2 inhibitor"
    studies = data_io.studies_for_treatment(net, t)
    yi = [s.yi for s in studies]
    vi = [s.sei ** 2 for s in studies]
    grid = specs.grid_for_contrast(yi, vi)
    assert len(grid) == 9  # 4 tau2 x 2 CI (additive) + 1 multiplicative
    fe = [s for s in grid if s["estimator"] == "FE"]
    assert all(s["tau2"] == 0.0 for s in fe)
    mult = [s for s in grid if s["het_model"] == "multiplicative"]
    assert len(mult) == 1 and mult[0]["phi"] >= 1.0


def test_hksj_never_narrower_than_wald(net):
    t = "SGLT2 inhibitor"
    studies = data_io.studies_for_treatment(net, t)
    yi = [s.yi for s in studies]
    vi = [s.sei ** 2 for s in studies]
    wald = specs.pool_one(yi, vi, "DL", "Wald")
    hksj = specs.pool_one(yi, vi, "DL", "HKSJ")
    w_wald = wald["ci_high"] - wald["ci_low"]
    w_hksj = hksj["ci_high"] - hksj["ci_low"]
    assert w_hksj >= w_wald - 1e-9  # q>=1 floor


# ---- SUCRA / POTH ----------------------------------------------------------

def test_sucra_and_poth_ranges():
    effects = {"A": (0.0, 0.0), "B": (0.5, 0.01), "C": (-0.5, 0.01)}
    s = ranking.sucra(effects)
    assert all(0.0 <= v <= 1.0 for v in s.values())
    p = ranking.poth(effects)
    assert 0.0 <= p <= 1.0


def test_poth_high_when_well_separated():
    # widely separated, tiny variance -> hierarchy almost certain
    effects = {"A": (0.0, 1e-4), "B": (2.0, 1e-4), "C": (4.0, 1e-4)}
    assert ranking.poth(effects, n=5000, seed=1) > 0.95


def test_poth_low_when_overlapping():
    effects = {"A": (0.0, 1.0), "B": (0.05, 1.0), "C": (0.1, 1.0)}
    assert ranking.poth(effects, n=5000, seed=1) < 0.5


def test_poth_seed_deterministic():
    effects = {"A": (0.0, 0.1), "B": (0.3, 0.1)}
    assert ranking.poth(effects, n=3000, seed=7) == ranking.poth(effects, n=3000, seed=7)


# ---- the C2 cardinal sin ---------------------------------------------------

def test_weighted_likelihood_wider_than_ivre(rep):
    # IV-RE pooling of S specs from ONE dataset collapses the CI; weighted-
    # likelihood must be wider for every contrast (the false-robustness guard).
    for t, c in rep["per_contrast"].items():
        assert c["ci_width_wl"] > c["ci_width_ivre"], t


def test_ivre_manufactures_significance(rep):
    # On this network at least one contrast flips robust(IVRE)->fragile(WL).
    flips = [t for t, c in rep["per_contrast"].items()
             if c["naive_ivre_pool"]["significant"] and not c["weighted_likelihood"]["significant"]]
    assert flips  # GLP-1 RA and/or SGLT2


def test_hierarchy_non_informative_gate(rep):
    # aggregated POTH < 0.5 -> hierarchy non-informative on this network
    ah = rep["aggregated_hierarchy"]
    assert ah["poth"] < 0.5
    assert ah["informative"] is False


def test_phase2_matches_baseline(rep):
    import json
    from pathlib import Path
    base = json.loads((Path(__file__).parent / "fixtures" / "phase2_baseline.json")
                      .read_text(encoding="utf-8"))
    assert rep["n_network_specs"] == base["n_network_specs"]
    assert rep["best_treatment_distribution"] == base["best_treatment_distribution"]
    for t, v in base["per_contrast_verdicts"].items():
        assert rep["per_contrast"][t]["weighted_likelihood"]["verdict"] == v["wl"]
        assert rep["per_contrast"][t]["naive_ivre_pool"]["verdict"] == v["ivre"]
    ah, bh = rep["aggregated_hierarchy"], base["aggregated_hierarchy"]
    assert ah["order"] == bh["order"]
    assert ah["poth"] == pytest.approx(bh["poth"], abs=1e-4)  # seeded MC -> deterministic
    assert ah["informative"] == bh["informative"]
    # new extension axes
    for t, choice in base["het_model_choice"].items():
        assert rep["het_model_choice"][t]["choice"] == choice
    pb = rep["pub_bias_robma"]
    assert pb["k"] == base["pub_bias_robma"]["k"]
    assert pb["underpowered"] == base["pub_bias_robma"]["underpowered"]
    assert pb["model_averaged"]["significant"] == base["pub_bias_robma"]["model_averaged_significant"]
