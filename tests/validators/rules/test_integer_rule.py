"""Tests for the integer_rule composition factory."""

from simplibs.rules.testing import assert_rule_contract
from simplibs.validate.validators.rules import integer_rule


def test_integer_rule_default_contract(subtests):
    """Verify default integer_rule (acts purely as is_integer check)."""
    assert_rule_contract(
        subtests,
        rule=integer_rule(),
        valid_values=[0, 42, -100],
        invalid_values=[3.14, True, False, "123", None, [1]],
        rule_factory=integer_rule,
        deep_check=True,
        verbose=False,
    )


def test_integer_rule_ranges_and_divisibility(subtests):
    """Verify integer_rule with range, sign, divisibility, and set membership."""
    assert_rule_contract(
        subtests,
        rule=integer_rule(
            positive=True,
            in_range=(1, 100),
            divisible_by=3,
            has_remainder=(5, 1),  # value % 5 == 1 -> e.g. 6, 21, 36, 51, 66, 81, 96
            is_in={6, 21, 36, 51},
            not_equals=21,
        ),
        valid_values=[6, 36, 51],
        invalid_values=[
            21,      # Fails not_equals
            9,       # Fails has_remainder
            12,      # Fails possesses remainder check & fails is_in
            -6,      # Fails positive
            102,     # Outside in_range
        ],
        deep_check=True,
        verbose=False,
    )


def test_integer_rule_negative_flag(subtests):
    """Verify negative=True means strictly below zero (zero itself is not negative)."""
    assert_rule_contract(
        subtests,
        rule=integer_rule(negative=True),
        valid_values=[-1, -50],
        invalid_values=[0, 5, -1.5],
        deep_check=True,
        verbose=False,
    )


def test_integer_rule_greater_or_equal(subtests):
    """Verify greater_or_equal includes the bound itself."""
    assert_rule_contract(
        subtests,
        rule=integer_rule(greater_or_equal=5),
        valid_values=[5, 6],
        invalid_values=[4, -1],
        deep_check=True,
        verbose=False,
    )


def test_integer_rule_less_than(subtests):
    """Verify less_than excludes the bound itself."""
    assert_rule_contract(
        subtests,
        rule=integer_rule(less_than=5),
        valid_values=[4, -1],
        invalid_values=[5, 6],
        deep_check=True,
        verbose=False,
    )


def test_integer_rule_less_or_equal(subtests):
    """Verify less_or_equal includes the bound itself."""
    assert_rule_contract(
        subtests,
        rule=integer_rule(less_or_equal=5),
        valid_values=[5, 4],
        invalid_values=[6, 10],
        deep_check=True,
        verbose=False,
    )


def test_integer_rule_equals(subtests):
    """Verify equals accepts only the exact integer."""
    assert_rule_contract(
        subtests,
        rule=integer_rule(equals=7),
        valid_values=[7],
        invalid_values=[8, 0, 7.5],
        deep_check=True,
        verbose=False,
    )


def test_integer_rule_not_in(subtests):
    """Verify not_in rejects the listed integers."""
    assert_rule_contract(
        subtests,
        rule=integer_rule(not_in={1, 2}),
        valid_values=[3, 0],
        invalid_values=[1, 2],
        deep_check=True,
        verbose=False,
    )
