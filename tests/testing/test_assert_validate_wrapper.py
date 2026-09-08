"""Tests for the assert_validate_wrapper testing utility."""

import pytest
from typing import Any
from simplibs.validate.testing import assert_validate_wrapper
from simplibs.validate.validators import validate_str
from simplibs.validate.validators.rules import string_rule


def test_assert_validate_wrapper_happy_path(subtests):
    """Verify that a compliant wrapper function passes contract assertion."""
    assert_validate_wrapper(
        subtests,
        validate_func=validate_str,
        rule_factory=string_rule,
        valid_value="user_admin",
        invalid_value=123,
        sample_params={"starts_with": "user_"},
        verbose=False,
    )


def test_assert_validate_wrapper_detects_missing_param(subtests):
    """Verify that assert_validate_wrapper fails if wrapper lacks a parameter."""

    def dummy_rule_factory(*, min_length: int | None = None):
        pass

    def broken_validate(value: Any, *, value_name=None, context=None, return_bool=False, return_value=False):
        pass

    with pytest.raises(AssertionError, match="Param 'min_length'"):
        assert_validate_wrapper(
            subtests,
            validate_func=broken_validate,
            rule_factory=dummy_rule_factory,
            valid_value="a",
            invalid_value=1,
            verbose=False,
        )