"""P0-B coverage tests: PI computation, the C1 'never default to conformal'
guardrail, and known-truth simulation determinism / direction."""

import math

import pytest

from phase1 import coverage, data_io


@pytest.fixture(scope="module")
def net():
    return data_io.load_network()


def test_intervals_computable_on_real_network(net):
    yi, sei = data_io.active_vs_placebo_sample(net)
    iv = coverage.compute_intervals(yi, sei)
    assert iv["computable"] and iv["k"] == 10
    assert iv["theta"] == pytest.approx(0.0696, abs=5e-3)
    for m in ("conformal", "standard", "hksj"):
        lo, hi = iv["intervals"][m]
        assert lo < hi and iv["widths"][m] > 0


def test_recommend_never_defaults_to_conformal_when_standard_qualifies():
    # standard meets nominal AND is narrowest -> must be chosen over conformal
    cov = {"conformal": 0.99, "standard": 0.96, "hksj": 0.94}
    iv = {"widths": {"conformal": 0.80, "standard": 0.50, "hksj": 0.45}}
    rec = coverage.recommend_pi(cov, iv)
    assert rec["meets_nominal"] is True
    assert rec["recommended"] == "standard"  # narrowest qualifier, not conformal


def test_recommend_reports_undercoverage_honestly():
    cov = {"conformal": 0.90, "standard": 0.90, "hksj": 0.90}
    iv = {"widths": {"conformal": 0.71, "standard": 0.50, "hksj": 0.49}}
    rec = coverage.recommend_pi(cov, iv)
    assert rec["meets_nominal"] is False
    assert "under-cover" in rec["note"]


def test_known_truth_sim_is_seed_deterministic(net):
    _, sei = data_io.active_vs_placebo_sample(net)
    a = coverage.simulate_coverage(0.07, 0.011, sei, n_sims=500, seed=1)
    b = coverage.simulate_coverage(0.07, 0.011, sei, n_sims=500, seed=1)
    assert a["by_method"]["conformal"]["coverage"] == b["by_method"]["conformal"]["coverage"]


def test_known_truth_sim_direction_small_k(net):
    # At k=10 under a correctly-specified normal RE model: standard/HKSJ
    # under-cover; conformal is no worse than them (the honest no-free-lunch
    # result). Assert robust ordering, not brittle point values.
    _, sei = data_io.active_vs_placebo_sample(net)
    sim = coverage.simulate_coverage(0.07, 0.011, sei, n_sims=2000, seed=20260620)
    cov = {m: sim["by_method"][m]["coverage"] for m in ("conformal", "standard", "hksj")}
    assert cov["standard"] < 0.95  # standard under-covers at small k
    assert cov["conformal"] >= cov["hksj"]  # conformal not worse than hksj
    assert all(0.85 <= v <= 1.0 for v in cov.values())
