"""Tests for the validated_type utility function."""

from typing import Annotated, Any, get_args, get_origin
import pytest

from simplibs.exception import ParamError, ValidationError
from simplibs.rules import Rule
from simplibs.validate.testing import assert_type_contract
from simplibs.validate.tools import validated_type


class DummyPositiveRule(Rule):
    """Simple rule checking if integer is positive."""

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


def test_validated_type_constructs_annotated_with_rule():
    """Verify that validated_type constructs correct Annotated with a Rule instance."""
    rule = DummyPositiveRule()
    target_type = validated_type(int, rule)

    assert get_origin(target_type) is Annotated
    args = get_args(target_type)
    assert args[0] is int
    assert args[1] is rule


def test_validated_type_constructs_annotated_with_callable():
    """Verify that validated_type accepts plain callable predicates."""

    def is_even(v: int) -> bool:
        return v % 2 == 0

    target_type = validated_type(int, is_even)

    assert get_origin(target_type) is Annotated
    args = get_args(target_type)
    assert args[0] is int
    assert args[1] is is_even


def test_validated_type_constructs_annotated_with_multiple_rules():
    """Verify that validated_type accepts multiple positional rules."""
    rule = DummyPositiveRule()

    def is_even(v: int) -> bool:
        return v % 2 == 0

    target_type = validated_type(int, rule, is_even)

    args = get_args(target_type)
    assert args[0] is int
    assert args[1] is rule
    assert args[2] is is_even


def test_validated_type_contract_integration(subtests):
    """Verify that a type built with validated_type satisfies the type contract."""
    rule = DummyPositiveRule()
    positive_int = validated_type(int, rule)

    assert_type_contract(
        subtests,
        type_=positive_int,
        valid_values=[1, 10, 100],
        invalid_values=[-5, 0],
        check_validate_call=True,
        verbose=False,
    )


def test_validated_type_raises_error_when_no_rules():
    """Verify that validated_type raises ParamError when zero rules are passed."""
    with pytest.raises(ParamError) as exc_info:
        validated_type(int)

    assert exc_info.value.error_name == "VALIDATED_TYPE_MISSING_RULE_ERROR"


@pytest.mark.parametrize(
    "invalid_rule, index",
    [
        ("not_a_rule", 0),
        (123, 0),
        (None, 1),
    ],
)
def test_validated_type_raises_error_on_invalid_rule(invalid_rule, index):
    """Verify that validated_type raises ParamError when any rule is invalid."""
    rule = DummyPositiveRule()

    rules = [rule, rule]
    rules[index] = invalid_rule

    with pytest.raises(ParamError) as exc_info:
        validated_type(int, *rules)

    assert exc_info.value.error_name == "VALIDATED_TYPE_RULE_INVALID_ERROR"