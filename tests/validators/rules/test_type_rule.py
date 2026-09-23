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