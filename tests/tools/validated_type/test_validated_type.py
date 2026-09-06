from typing import Annotated, get_args, get_origin
import pytest

# Tested function and exceptions
from simplibs.validate.exceptions import ParamError
from simplibs.validate.rules import greater_than, is_integer
from simplibs.validate.tools.validated_type.validated_type import validated_type


def test_validated_type_single_rule() -> None:
    """Verify that validated_type correctly builds Annotated construct with a single Rule."""
    rule = greater_than(0)
    res = validated_type(int, rule)

    assert get_origin(res) is Annotated
    assert get_args(res) == (int, rule)


def test_validated_type_multiple_rules() -> None:
    """Verify that validated_type handles multiple rules as separate Annotated metadata items."""
    rule1 = is_integer
    rule2 = greater_than(0)
    res = validated_type(int, rule1, rule2)

    assert get_origin(res) is Annotated
    assert get_args(res) == (int, rule1, rule2)


def test_validated_type_with_callable_predicate() -> None:
    """Verify that validated_type accepts plain callable predicates alongside Rule instances."""
    custom_pred = lambda v: v % 2 == 0
    rule = greater_than(0)
    res = validated_type(int, rule, custom_pred)

    assert get_origin(res) is Annotated
    assert get_args(res) == (int, rule, custom_pred)


def test_validated_type_missing_rule_error() -> None:
    """Verify that calling validated_type without any rules raises ParamError with error_name VALIDATED_TYPE_MISSING_RULE_ERROR."""
    with pytest.raises(ParamError) as exc_info:
        validated_type(int)

    assert exc_info.value.error_name == "VALIDATED_TYPE_MISSING_RULE_ERROR"


def test_validated_type_invalid_rule_error() -> None:
    """Verify that calling validated_type with an invalid rule raises ParamError with error_name VALIDATED_TYPE_RULE_INVALID_ERROR."""
    with pytest.raises(ParamError) as exc_info:
        validated_type(int, greater_than(0), "not_a_rule")

    assert exc_info.value.error_name == "VALIDATED_TYPE_RULE_INVALID_ERROR"