"""Tests for the validate_mapping high-level wrapper."""

from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_mapping
from simplibs.validate.validators.rules import mapping_rule


def test_validate_mapping_contract(subtests):
    """Verify validate_mapping wrapper contract and delegation."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_mapping,
        rule_factory=mapping_rule,
        valid_value={"key": "value"},
        invalid_value=["not_a_dict"],
        sample_params={"has_key": "key", "min_length": 1},
        verbose=False,
    )