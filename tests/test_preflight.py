"""Task 0 preflight tests."""

from phase1 import data_io, preflight


def test_dataset_loads_clean_k10():
    net = data_io.load_network()
    rows = data_io.contrasts(net)
    assert len(rows) == 10
    assert all(r.sei > 0 and r.yi == r.yi for r in rows)  # finite, positive SE
    assert data_io.reference(net) == "placebo"


def test_invalid_sei_fails_closed():
    net = data_io.load_network()
    net["contrasts"][0]["sei"] = 0.0  # zero SE must raise, never impute
    try:
        data_io.contrasts(net)
    except data_io.DataError:
        return
    raise AssertionError("expected DataError on sei=0")


def test_preflight_runnable_verdict():
    rep = preflight.run()
    # On any box the run must be at least UNVERIFIED (clean data); never FAIL here.
    assert rep["verdict"] in ("PASS", "UNVERIFIED")
    by = {r["check"]: r["status"] for r in rep["results"]}
    assert by["vendored_dataset"] == "pass"
