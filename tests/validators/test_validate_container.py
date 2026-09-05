"""Tests for the validate_container high-level wrapper."""

from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_container
from simplibs.validate.validators.rules import container_rule


def test_validate_container_contract(subtests):
    """Verify validate_container wrapper contract and delegation."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_container,
        rule_factory=container_rule,
        valid_value=[1, 2, 3],
        invalid_value="not_a_container_or_invalid_length",
        sample_params={"min_length": 1, "unique": True},
        verbose=False,
    )