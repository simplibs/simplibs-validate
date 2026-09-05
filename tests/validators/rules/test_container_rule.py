"""Tests for the container_rule composition factory."""

from simplibs.validate.rules import is_integer
from simplibs.validate.testing import assert_rule_contract
from simplibs.validate.validators.rules import container_rule


def test_container_rule_default_contract(subtests):
    """Verify default container_rule (acts purely as is_container check)."""
    assert_rule_contract(
        subtests,
        rule=container_rule(),
        valid_values=[[1, 2], (1, 2), {1, 2}, {"a": 1}],
        invalid_values=[123, 45.6, True, None, "hello"],
        rule_factory=container_rule,
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_container_rule_length_constraints(subtests):
    """Verify container_rule with length, min_length, and max_length constraints."""
    assert_rule_contract(
        subtests,
        rule=container_rule(min_length=2, max_length=4),
        valid_values=[[1, 2], (1, 2, 3), {1, 2, 3, 4}],
        invalid_values=[[1], [1, 2, 3, 4, 5]],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )

    assert_rule_contract(
        subtests,
        rule=container_rule(length=3),
        valid_values=[[1, 2, 3], (1, 2, 3)],
        invalid_values=[[1, 2], [1, 2, 3, 4]],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_container_rule_membership_and_uniqueness(subtests):
    """Verify container_rule with unique, has_item, subset_of, superset_of, and for_each."""
    assert_rule_contract(
        subtests,
        rule=container_rule(
            unique=True,
            has_item=2,
            subset_of={1, 2, 3, 4},
            superset_of={1, 2},
            for_each=is_integer,
        ),
        valid_values=[[1, 2, 3], (2, 1, 4)],
        invalid_values=[
            [1, 1, 2],       # Duplicate items
            [1, 3, 4],       # Missing item 2
            [1, 2, 5],       # 5 not in subset_of
            [2, 3],          # Missing 1 from superset_of
            [1, 2, "3"],     # Non-integer item
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_container_rule_invalid_init_parameters(subtests):
    """Verify that conflicting length parameters raise ParamError."""
    assert_rule_contract(
        subtests,
        rule=container_rule(),
        valid_values=[[1]],
        invalid_values=[123, None],
        rule_factory=container_rule,
        invalid_init_params=[
            ((), {"length": 3, "min_length": 1}),
            ((), {"length": 3, "max_length": 5}),
        ],
        verbose=False,
    )