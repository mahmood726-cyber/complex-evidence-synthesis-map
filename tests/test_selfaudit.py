"""P0-A CINeMA-6 self-audit tests, incl. the fail-closed no-substitution rule."""

import pytest

from phase1 import data_io, selfaudit


@pytest.fixture(scope="module")
def net():
    return data_io.load_network()


def test_heterogeneity_major_on_high_i2(net):
    d = selfaudit.assess_heterogeneity({**net["nma"]})
    assert d["level"] == "major_concern"  # I2 ~73%
    assert d["metrics"]["i2"] > 0.6
    assert "tau2" in d["metrics"]  # magnitude reported alongside the proportion


def test_within_study_bias_unassessed_not_assumed_low(net):
    # No risk_of_bias key -> MUST be 'unassessed' (downgrade), never 'no_concern'.
    d = selfaudit.assess_within_study_bias(net)
    assert d["level"] == "unassessed"
    assert d["level"] != "no_concern"


def test_within_study_bias_major_when_high_rob_provided():
    d = selfaudit.assess_within_study_bias({"risk_of_bias": {"high": 2, "some": 1, "low": 5}})
    assert d["level"] == "major_concern"


def test_reporting_bias_unassessed_when_missing(net):
    assert selfaudit.assess_reporting_bias(net)["level"] == "unassessed"


def test_incoherence_star_network_some_concern(net):
    # star network: not assessable -> some_concern (undetectable, not absent)
    assert selfaudit.assess_incoherence(net["nma"])["level"] == "some_concern"


def test_grade_all_clear_is_gold():
    domains = {k: {"level": "no_concern"} for k in
               ("heterogeneity", "imprecision", "incoherence",
                "indirectness", "within_study_bias", "reporting_bias")}
    g = selfaudit.grade(domains)
    assert g["certainty"] == "High" and g["badge"] == "Gold"


def test_grade_any_major_caps_at_bronze():
    domains = {k: {"level": "no_concern"} for k in
               ("imprecision", "incoherence", "indirectness",
                "within_study_bias", "reporting_bias")}
    domains["heterogeneity"] = {"level": "major_concern"}
    g = selfaudit.grade(domains)
    assert g["badge"] == "Bronze"
    assert g["has_major_concern"] is True


def test_full_verdict_on_network_is_bronze(net):
    v = selfaudit.cinema6_verdict(net, recommended_pi=(-0.286, 0.425))
    assert set(v["cinema6"]) == {"heterogeneity", "imprecision", "incoherence",
                                 "indirectness", "within_study_bias", "reporting_bias"}
    assert v["grade"]["badge"] == "Bronze"


def test_merge_preserves_existing_assurance_keys(net):
    existing = {"slug": "x", "tier": "silver", "checks": {"code_runs": "pass"}}
    merged = selfaudit.merge_into_assurance(existing, selfaudit.cinema6_verdict(net))
    assert merged["slug"] == "x" and merged["checks"]["code_runs"] == "pass"
    assert "cinema6" in merged and "cinema6_grade" in merged
