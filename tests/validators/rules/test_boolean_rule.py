"""Tests for the boolean_rule composition factory."""

from simplibs.rules.testing import assert_rule_contract
from simplibs.validate.validators.rules import boolean_rule


def test_boolean_rule_default_contract(subtests):
    """Verify default boolean_rule (acts purely as is_bool check)."""
    assert_rule_contract(
        subtests,
        rule=boolean_rule(),
        valid_values=[True, False],
        invalid_values=[1, 0, "True", None, [], {}],
        rule_factory=boolean_rule,
        deep_check=True,
        verbose=False,
    )


def test_boolean_rule_equals_true(subtests):
    """Verify boolean_rule with equals=True constraint."""
    assert_rule_contract(
        subtests,
        rule=boolean_rule(equals=True),
        valid_values=[True],
        invalid_values=[False, 1, 0, "True"],
        deep_check=True,
        verbose=False,
    )


def test_boolean_rule_equals_false(subtests):
    """Verify boolean_rule with equals=False constraint."""
    assert_rule_contract(
        subtests,
        rule=boolean_rule(equals=False),
        valid_values=[False],
        invalid_values=[True, 0, 1, "False"],
        deep_check=True,
        verbose=False,
    )