"""Tests for the float_rule composition factory."""

import math
import pytest
from simplibs.rules.testing import assert_rule_contract
from simplibs.validate.validators.rules import float_rule


def test_float_rule_default_contract(subtests):
    """Verify default float_rule (finite=True by default, excludes Inf and NaN)."""
    # 1. Base contract test with standard values (excluding NaN to avoid IEEE 754 nan == nan issue)
    assert_rule_contract(
        subtests,
        rule=float_rule(),
        valid_values=[0.0, 3.14, -42.5],
        invalid_values=[
            math.inf, -math.inf,
            10, "3.14", True, None,
        ],
        rule_factory=float_rule,
        deep_check=True,
        verbose=False,
    )

    # 2. Verify math.nan invalidation explicitly
    rule = float_rule()
    assert rule.is_valid(math.nan) is False


def test_float_rule_non_finite_allowed(subtests):
    """Verify float_rule with finite=False allowing NaN and Infinity."""
    # 1. Standard values contract test
    assert_rule_contract(
        subtests,
        rule=float_rule(finite=False),
        valid_values=[0.0, 3.14, math.inf, -math.inf],
        invalid_values=[10, "3.14", True, None],
        rule_factory=float_rule,
        deep_check=True,
        verbose=False,
    )

    # 2. Verify math.nan validity explicitly (avoiding nan == nan in deep_check)
    rule = float_rule(finite=False)
    assert rule.is_valid(math.nan) is True
    assert math.isnan(rule.validate(math.nan, return_value=True))


def test_float_rule_numeric_constraints(subtests):
    """Verify float_rule with range, signs, close_to, and set membership constraints."""
    assert_rule_contract(
        subtests,
        rule=float_rule(
            positive=True,
            greater_than=1.0,
            less_or_equal=10.0,
            close_to_target=5.0,
            close_to_abs_tol=0.5,
            not_equals=5.0,
        ),
        valid_values=[4.8, 5.2],
        invalid_values=[
            5.0,     # Fails not_equals
            0.5,     # Fails greater_than / close_to
            5.8,     # Outside close_to tolerance
            -2.0,    # Fails positive / greater_than
        ],
        deep_check=True,
        verbose=False,
    )