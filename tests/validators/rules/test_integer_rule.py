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