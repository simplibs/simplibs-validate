import pytest

# Tested function and exceptions
from simplibs.exception import ParamError
from simplibs.rules import greater_than, is_integer
from simplibs.rules.predicates.logic import UserRule
from simplibs.validate.tools import override_rules


def test_override_rules_empty() -> None:
    """Verify that calling override_rules with no kwargs returns an empty dictionary."""
    res = override_rules()
    assert res == {}


def test_override_rules_with_rule_instances() -> None:
    """Verify that override_rules keeps Rule instances as-is."""
    rule1 = is_integer
    rule2 = greater_than(0)

    res = override_rules(param1=rule1, param2=rule2)

    assert res == {"param1": rule1, "param2": rule2}


def test_override_rules_wraps_callable_in_user_rule() -> None:
    """Verify that override_rules automatically wraps plain callables in UserRule instances."""
    custom_pred = lambda v: v > 0

    res = override_rules(param=custom_pred)

    assert "param" in res
    assert isinstance(res["param"], UserRule)
    # Verify wrapped rule functionality directly via its evaluation
    assert res["param"].is_valid(5) is True
    assert res["param"].is_valid(-1) is False


def test_override_rules_mixed_rules_and_callables() -> None:
    """Verify that override_rules handles a mix of Rule instances and callable predicates."""
    rule = greater_than(10)
    custom_pred = lambda v: v % 2 == 0

    res = override_rules(param1=rule, param2=custom_pred)

    assert res["param1"] is rule
    assert isinstance(res["param2"], UserRule)


def test_override_rules_invalid_value_error() -> None:
    """Verify that calling override_rules with an invalid rule value raises ParamError."""
    with pytest.raises(ParamError) as exc_info:
        override_rules(param1=greater_than(0), param2="not_a_rule")

    assert exc_info.value.error_name == "OVERRIDE_RULES_INVALID_ERROR"
    assert exc_info.value.label == "param2"