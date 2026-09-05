"""Tests for the validate_type high-level wrapper."""

from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_type
from simplibs.validate.validators.rules import type_rule


def test_validate_type_contract(subtests):
    """Verify validate_type wrapper contract and delegation."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_type,
        rule_factory=type_rule,
        valid_value=ValueError,
        invalid_value="not_a_type_instance",
        sample_params={"subclass_of": (Exception,)},
        verbose=False,
    )