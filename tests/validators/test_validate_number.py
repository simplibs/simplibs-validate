"""Tests for the validate_number high-level wrapper."""

from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_number
from simplibs.validate.validators.rules import number_rule


def test_validate_number_contract(subtests):
    """Verify validate_number wrapper contract and delegation."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_number,
        rule_factory=number_rule,
        valid_value=42,
        invalid_value="not_a_number",
        sample_params={"greater_than": 0, "positive": True},
        verbose=False,
    )