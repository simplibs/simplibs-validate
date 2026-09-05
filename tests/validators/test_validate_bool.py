"""Tests for the validate_bool high-level wrapper."""

from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_bool
from simplibs.validate.validators.rules import boolean_rule


def test_validate_bool_contract(subtests):
    """Verify validate_bool wrapper contract and delegation."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_bool,
        rule_factory=boolean_rule,
        valid_value=True,
        invalid_value="not_a_bool",
        sample_params={"equals": True},
        verbose=False,
    )