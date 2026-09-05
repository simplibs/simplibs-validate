"""Tests for the validate_int high-level wrapper."""

from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_int
from simplibs.validate.validators.rules import integer_rule


def test_validate_int_contract(subtests):
    """Verify validate_int wrapper contract and delegation."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_int,
        rule_factory=integer_rule,
        valid_value=10,
        invalid_value="10_as_string",
        sample_params={"greater_than": 0, "divisible_by": 2},
        verbose=False,
    )