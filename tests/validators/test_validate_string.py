"""Tests for the validate_string high-level wrapper."""

from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_string
from simplibs.validate.validators.rules import string_rule


def test_validate_string_contract(subtests):
    """Verify validate_string wrapper contract and delegation."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_string,
        rule_factory=string_rule,
        valid_value="hello_world",
        invalid_value=12345,
        sample_params={"starts_with": "hello_", "min_length": 5},
        verbose=False,
    )