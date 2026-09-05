"""Tests for the validate_float high-level wrapper."""

from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_float
from simplibs.validate.validators.rules import float_rule


def test_validate_float_contract(subtests):
    """Verify validate_float wrapper contract and delegation."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_float,
        rule_factory=float_rule,
        valid_value=10.5,
        invalid_value="not_a_float",
        sample_params={"greater_than": 5.0, "positive": True},
        verbose=False,
    )