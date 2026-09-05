"""Tests for the number_rule composition factory."""

from decimal import Decimal
from simplibs.validate.testing import assert_rule_contract
from simplibs.validate.validators.rules import number_rule


def test_number_rule_default_contract(subtests):
    """Verify default number_rule (accepts int, float, Decimal, complex; excludes bool)."""
    assert_rule_contract(
        subtests,
        rule=number_rule(),
        valid_values=[10, 3.14, Decimal("42.5"), complex(1, 2)],
        invalid_values=[True, False, "123", None, [10]],
        rule_factory=number_rule,
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_number_rule_numeric_constraints(subtests):
    """Verify number_rule with range, signs, and membership across numeric types."""
    assert_rule_contract(
        subtests,
        rule=number_rule(
            positive=True,
            less_or_equal=100,
            not_equals=50,
            not_in={13, 66},
        ),
        valid_values=[1, 3.14, Decimal("42"), 99.9],
        invalid_values=[
            0,            # Fails positive
            -10,          # Fails positive
            50,           # Fails not_equals
            13,           # Fails not_in
            150,          # Fails less_or_equal
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )