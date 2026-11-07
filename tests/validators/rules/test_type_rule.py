"""Tests for the type_rule composition factory."""

from simplibs.rules.testing import assert_rule_contract
from simplibs.validate.validators.rules import type_rule


class BaseService:
    pass


class AuthService(BaseService):
    pass


class UnrelatedClass:
    pass


def test_type_rule_default_contract(subtests):
    """Verify default type_rule (acts purely as is_type check)."""
    assert_rule_contract(
        subtests,
        rule=type_rule(),
        valid_values=[int, str, BaseService, object],
        invalid_values=[123, "str", BaseService(), None],
        rule_factory=type_rule,
        deep_check=True,
        verbose=False,
    )


def test_type_rule_subclass_and_membership(subtests):
    """Verify type_rule with subclass_of and set constraints."""
    assert_rule_contract(
        subtests,
        rule=type_rule(
            subclass_of=(BaseService,),
            not_equals=BaseService,
        ),
        valid_values=[AuthService],
        invalid_values=[
            BaseService,     # Fails not_equals
            UnrelatedClass,  # Fails subclass_of
            int,             # Fails subclass_of
            "AuthService",   # Not a type
        ],
        deep_check=True,
        verbose=False,
    )


def test_type_rule_equals(subtests):
    """Verify equals accepts only that exact class (a subclass or a look-alike is not equal)."""
    assert_rule_contract(
        subtests,
        rule=type_rule(equals=BaseService),
        valid_values=[BaseService],
        invalid_values=[AuthService, UnrelatedClass, int, "BaseService"],
        deep_check=True,
        verbose=False,
    )


def test_type_rule_is_in(subtests):
    """Verify is_in accepts only the listed classes."""
    assert_rule_contract(
        subtests,
        rule=type_rule(is_in={int, str}),
        valid_values=[int, str],
        invalid_values=[float, bool, "int", 5],
        deep_check=True,
        verbose=False,
    )


def test_type_rule_not_in(subtests):
    """Verify not_in rejects the listed classes but still requires a class object."""
    assert_rule_contract(
        subtests,
        rule=type_rule(not_in={int, str}),
        valid_values=[float, BaseService],
        invalid_values=[int, str, 5, "int"],
        deep_check=True,
        verbose=False,
    )
