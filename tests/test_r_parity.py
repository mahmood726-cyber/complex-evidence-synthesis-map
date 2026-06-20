"""B1: pooling backbone vs metafor. Skips when R/metafor is unavailable so the
suite stays green on R-less boxes (the run is then UNVERIFIED, not failed)."""

import pytest

from phase1 import bootstrap, data_io
from phase2 import validate_r

pytestmark = pytest.mark.skipif(
    bootstrap.find_rscript() is None, reason="Rscript not available")


def test_pooling_matches_metafor():
    res = validate_r.validate(data_io.load_network())
    assert res is not None
    if res.get("skipped"):
        pytest.skip(res["reason"])
    assert res["rows"]
    for r in res["rows"]:
        assert r["d_b"] < 1e-5, f"{r['contrast']}/{r['method']} estimate drift {r['d_b']:.2e}"
        assert r["d_se"] < 1e-5, f"{r['contrast']}/{r['method']} SE drift {r['d_se']:.2e}"
