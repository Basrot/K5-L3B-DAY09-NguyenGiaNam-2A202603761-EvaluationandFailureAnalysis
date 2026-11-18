"""Regression case: a ticket delay must not override the order row."""

import pytest

from lab9.trace_case import investigate


@pytest.mark.student
def test_c002_ticket_override_changes_refund():
    broken = investigate("seeded_regression", "C-002", 11)["trial"]
    fixed = investigate("fixed", "C-002", 11)["trial"]
    assert broken["events"][2]["kind"] == "model_override"
    assert broken["snapshot"]["refund_vnd"] == 20_000
    assert broken["lab8_pass"] is False
    assert fixed["snapshot"]["refund_vnd"] == 0
    assert fixed["lab8_pass"] is True
