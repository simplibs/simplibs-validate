"""Tests for the master assert_type_contract orchestrator function."""

from typing import Annotated, Any
import pytest
from _pytest.outcomes import Failed

from simplibs.exception import ValidationError
from simplibs.rules import Rule
from simplibs.validate.testing import assert_type_contract


class DummyPositiveIntRule(Rule):
    """Rule checking positive integer values."""

    def is_valid(self, value: Any) -> bool:
        return isinstance(value, int) and value > 0

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        return ValidationError(
            problem="Value must be positive integer.",
            expected="Integer > 0.",
            how_to_fix="Provide positive integer.",
            label=value_name,
            value=value,
            context=context,
            error_name="NOT_POSITIVE_INT",
            exception=ValueError,
        )


ValidAnnotatedType = Annotated[int, DummyPositiveIntRule()]


class DummyCompoundRule(Rule):
    """Rule returning different error names and exception types based on value."""

    def is_valid(self, value: Any) -> bool:
        return False

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        if isinstance(value, str):
            err_name = "TYPE_ERROR"
            exc_type = TypeError
        else:
            err_name = "RANGE_ERROR"
            exc_type = ValueError

        return ValidationError(
            problem="Invalid value.",
            expected="Valid value.",
            how_to_fix="Fix value.",
            label=value_name,
            value=value,
            context=context,
            error_name=err_name,
            exception=exc_type,
        )


CompoundAnnotatedType = Annotated[Any, DummyCompoundRule()]


class DummyBrokenTypeRule(Rule):
    """Rule returning unexpected error_name in exception."""

    def is_valid(self, value: Any) -> bool:
        return isinstance(value, int) and value > 0

    def build_exception(
        self, value: Any, value_name: str = "value", context: str = ""
    ) -> ValidationError:
        return ValidationError(
            problem="Error",
            expected="5",
            how_to_fix="Provide 5",
            label=value_name,
            value=value,
            context=context,
            error_name="ACTUAL_ERROR_NAME",
        )


BrokenAnnotatedType = Annotated[int, DummyBrokenTypeRule()]


def test_assert_type_contract_full_success(subtests):
    """Verify complete successful orchestrator execution."""
    assert_type_contract(
        subtests,
        type_=ValidAnnotatedType,
        valid_values=[1, 42],
        invalid_values=[-1, 0],
        expected_error_name="NOT_POSITIVE_INT",
        expected_exception_type=ValueError,
        check_validate_call=True,
        deep_check=True,
        verbose=False,
    )


def test_assert_type_contract_sequence_metadata_success(subtests):
    """Verify sequence-based expected_error_name and expected_exception_type through orchestrator."""
    assert_type_contract(
        subtests,
        type_=CompoundAnnotatedType,
        valid_values=[],
        invalid_values=["bad_str", -10],
        expected_error_name=["TYPE_ERROR", "RANGE_ERROR"],
        expected_exception_type=[TypeError, ValueError],
        check_validate_call=True,
        deep_check=True,
        verbose=False,
    )


def test_assert_type_contract_without_validate_call_check(subtests):
    """Verify execution when check_validate_call is disabled."""
    assert_type_contract(
        subtests,
        type_=ValidAnnotatedType,
        valid_values=[1, 42],
        invalid_values=[-1, 0],
        check_validate_call=False,
        verbose=False,
    )


def test_assert_type_contract_fails_on_rule_contract_mismatch(subtests):
    """Verify that rule-level mismatches fail the orchestrator assertion."""
    with pytest.raises((AssertionError, Failed)):
        assert_type_contract(
            subtests,
            type_=BrokenAnnotatedType,
            valid_values=[1],
            invalid_values=[-1],
            expected_error_name="EXPECTED_ERROR_NAME",  # Mismatches ACTUAL
            verbose=False,
        )