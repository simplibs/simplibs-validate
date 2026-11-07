"""Tests for the number_rule composition factory."""

from decimal import Decimal
from simplibs.rules.testing import assert_rule_contract
from simplibs.validate.validators.rules import number_rule


def test_number_rule_default_contract(subtests):
    """Verify default number_rule (accepts int, float, Decimal, complex; excludes bool)."""
    assert_rule_contract(
        subtests,
        rule=number_rule(),
        valid_values=[10, 3.14, Decimal("42.5"), complex(1, 2)],
        invalid_values=[True, False, "123", None, [10]],
        rule_factory=number_rule,
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
        deep_check=True,
        verbose=False,
    )


def test_number_rule_negative_flag(subtests):
    """Verify negative=True means strictly below zero across numeric types."""
    assert_rule_contract(
        subtests,
        rule=number_rule(negative=True),
        valid_values=[-1, -0.5, Decimal("-3")],
        invalid_values=[0, 1, Decimal("2"), "-1"],
        deep_check=True,
        verbose=False,
    )


def test_number_rule_greater_or_equal(subtests):
    """Verify greater_or_equal includes the bound itself across numeric types."""
    assert_rule_contract(
        subtests,
        rule=number_rule(greater_or_equal=5),
        valid_values=[5, 5.5, Decimal("6")],
        invalid_values=[4, 4.9, Decimal("1")],
        deep_check=True,
        verbose=False,
    )


def test_number_rule_less_than(subtests):
    """Verify less_than excludes the bound itself across numeric types."""
    assert_rule_contract(
        subtests,
        rule=number_rule(less_than=5),
        valid_values=[4, 4.5, Decimal("-1")],
        invalid_values=[5, 5.1, Decimal("9")],
        deep_check=True,
        verbose=False,
    )


def test_number_rule_in_range_is_inclusive(subtests):
    """Verify in_range=(min, max) accepts both bounds across numeric types."""
    assert_rule_contract(
        subtests,
        rule=number_rule(in_range=(1, 10)),
        valid_values=[1, 5.5, Decimal("10")],
        invalid_values=[0, 10.5, Decimal("11")],
        deep_check=True,
        verbose=False,
    )


def test_number_rule_equals(subtests):
    """Verify equals accepts numerically equal values of different numeric types."""
    assert_rule_contract(
        subtests,
        rule=number_rule(equals=5),
        valid_values=[5, 5.0, Decimal("5")],
        invalid_values=[6, 4.9],
        deep_check=True,
        verbose=False,
    )


def test_number_rule_is_in(subtests):
    """Verify is_in accepts only the listed numbers."""
    assert_rule_contract(
        subtests,
        rule=number_rule(is_in={1, 2.5}),
        valid_values=[1, 2.5],
        invalid_values=[3, 0],
        deep_check=True,
        verbose=False,
    )


def test_number_rule_comparison_with_complex_is_invalid_not_a_crash(subtests):
    """Verify complex numbers (not orderable) are reported as invalid instead of raising."""
    assert_rule_contract(
        subtests,
        rule=number_rule(greater_than=0),
        valid_values=[1, 2.5, Decimal("3")],
        invalid_values=[complex(1, 2), 0, -1],
        deep_check=True,
        verbose=False,
    )
