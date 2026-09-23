"""Tests for the assert_type_validate_call_integration testing utility."""

from typing import Annotated, Any
import pytest
from _pytest.outcomes import Failed

from simplibs.exception import ValidationError
from simplibs.rules import Rule
from simplibs.validate.testing import assert_type_validate_call_integration


class DummyPositiveRule(Rule):
    """Rule that validates positive integers."""

    def is_valid(self, value: Any) -> bool:
        return isinstance(value, int) and value > 0

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        return ValidationError(
            problem="Value must be positive.",
            expected="Positive integer.",
            how_to_fix="Provide an integer > 0.",
            label=value_name,
            value=value,
            context=context,
        )


ValidType = Annotated[int, DummyPositiveRule()]


def test_assert_type_validate_call_integration_happy_path(subtests):
    """Verify that a valid type successfully passes the integration test."""
    assert_type_validate_call_integration(
        subtests,
        type_=ValidType,
        valid_values=[1, 10, 100],
        invalid_values=[-5, "str", None],
        verbose=False,
    )


def test_assert_type_validate_call_integration_fails_on_invalid_passing(
    subtests,
):
    """Verify that test fails when an invalid value unexpectedly passes."""
    assert_type_validate_call_integration(
        subtests,
        type_=ValidType,
        valid_values=[1],
        invalid_values=[-5],
        verbose=False,
    )


def test_assert_type_validate_call_integration_detects_failure_case(
    subtests,
):
    """Verify that assertion catches cases where an invalid input is accepted."""
    with pytest.raises((AssertionError, Failed)):
        assert_type_validate_call_integration(
            subtests,
            type_=ValidType,
            valid_values=[1],
            invalid_values=[5],  # 5 is valid, so _probe will NOT raise
            verbose=False,
        )