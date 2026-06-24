"""RoBMA-in-R cross-check of the portable pub-bias model-averaging. Skips when
JAGS/RoBMA is unavailable (run stays UNVERIFIED for this component, not failed)."""

import pytest

from phase2 import validate_robma


def test_robma_matches_portable_or_skips():
    res = validate_robma.validate()
    if res.get("skipped"):
        pytest.skip(res["reason"])
    # when RoBMA can run, model-averaged mu should be in the same ballpark as the
    # portable analog (both summarise the same pub-bias model set)
    assert res["abs_diff"] < 0.10
