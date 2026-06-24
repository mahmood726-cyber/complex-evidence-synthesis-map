"""Loop-containing NMA: core_ad on a triangle (direct+indirect) and the
node-split consistency check that a star network cannot support."""

import pytest

from phase2 import loop_network as L


def test_consistent_triangle_recovers_truth():
    rows = L.make_triangle(d_b=0.5, d_c=0.9, inconsistency=0.0)
    fm = L.fit(rows)
    # uses direct A-B/A-C + indirect (via B-C) evidence
    assert fm.treatment_effects["B"] == pytest.approx(0.5, abs=0.15)
    assert fm.treatment_effects["C"] == pytest.approx(0.9, abs=0.15)
    assert set(fm.parameter_treatments) == {"B", "C"}


def test_node_split_is_assessable_on_a_loop():
    rows = L.make_triangle(inconsistency=0.0)
    ns = L.node_split_bc(rows)
    assert ns["assessable"] is True          # the whole point vs the star network


def test_consistent_network_passes_node_split():
    ns = L.node_split_bc(L.make_triangle(inconsistency=0.0))
    assert ns["inconsistent"] is False and ns["p"] > 0.05


def test_injected_inconsistency_is_detected():
    ns = L.node_split_bc(L.make_triangle(inconsistency=0.6))
    assert ns["inconsistent"] is True and ns["p"] < 0.05


def test_inconsistency_inflates_tau():
    tau_con = L.fit(L.make_triangle(inconsistency=0.0)).tau
    tau_inc = L.fit(L.make_triangle(inconsistency=0.6)).tau
    assert tau_inc > tau_con
