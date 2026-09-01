"""Tests for the IsIn rule."""

from typing import Any
import pytest

from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.validate.testing import assert_rule_contract
from simplibs.validate.exceptions import ValidateError
from simplibs.validate.rules.predicates.logic import IsIn


def test_is_in_contract(subtests):
    """Verify the complete contract of the IsIn rule."""
    options = [1, 2, "admin", None]
    rule = IsIn(options)

    assert_rule_contract(
        subtests,
        rule=rule,
        valid_values=[1, 2, "admin", None],
        invalid_values=[3, "user", [1]],  # [1] triggers unhashable fallback/invalid test
        invalid_init_params=[
            ((123,), {}),       # Scalar is not a container -> ParamError
            (("string",), {}),  # String is not an allowed container -> ParamError
            ((None,), {}),      # None is not a container -> ParamError
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_is_in_exception_value_missing(subtests):
    """Verify diagnosis (ValueError) when value is missing from collection."""
    options = ["draft", "published"]
    rule = IsIn(options)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("archived", Kwargs(value_name="status")),
        exception_type=ValidateError,
        label="status",
        value="archived",
        error_name="IS_IN_ERROR",
        expected="one of ['draft', 'published']",
        problem="Value 'archived' is not one of ['draft', 'published'].",
        how_to_fix="Provide a value contained in ['draft', 'published'].",
        exception=ValueError,
        verbose=False,
    )


def test_is_in_exception_unhashable_value(subtests):
    """Verify diagnosis (TypeError) when value is unhashable against a set."""
    options = {1, 2, 3}
    rule = IsIn(options)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=([1, 2], Kwargs(value_name="payload")),
        exception_type=ValidateError,
        label="payload",
        value=[1, 2],
        error_name="IS_IN_ERROR",
        expected="one of {1, 2, 3}",
        problem="Value [1, 2] of type 'list' cannot be looked up in container 'set'.",
        how_to_fix="Provide a hashable value (e.g. tuple instead of list) or a compatible container.",
        exception=TypeError,
        verbose=False,
    )


def test_is_in_large_container_truncation(subtests):
    """Verify representation truncation for large containers (>60 characters)."""
    large_list = list(range(100))
    rule = IsIn(large_list)

    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=(999, Kwargs(value_name="id")),
        exception_type=ValidateError,
        label="id",
        value=999,
        error_name="IS_IN_ERROR",
        expected="one of list(size=100)",
        problem="Value 999 is not one of list(size=100).",
        how_to_fix="Provide a value contained in list(size=100).",
        exception=ValueError,
        verbose=False,
    )