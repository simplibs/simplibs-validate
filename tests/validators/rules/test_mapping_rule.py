"""Tests for the mapping_rule composition factory."""

from simplibs.sentinels import UNSET
from simplibs.validate.testing import assert_rule_contract
from simplibs.validate.validators.rules import mapping_rule


def test_mapping_rule_default_contract(subtests):
    """Verify default mapping_rule (acts purely as isinstance(dict) check)."""
    assert_rule_contract(
        subtests,
        rule=mapping_rule(),
        valid_values=[{}, {"a": 1}],
        invalid_values=[[("a", 1)], "a:1", None, 123, {1, 2}],
        rule_factory=mapping_rule,
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_mapping_rule_has_key_none_sentinel_distinction(subtests):
    """Verify that has_key=None works correctly and is distinct from UNSET."""
    # Dict MUST contain the explicit key `None`
    assert_rule_contract(
        subtests,
        rule=mapping_rule(has_key=None),
        valid_values=[{None: "value"}, {None: 1, "a": 2}],
        invalid_values=[{}, {"a": 2}],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_mapping_rule_keys_and_length_constraints(subtests):
    """Verify mapping_rule with keys requirement and length constraints."""
    assert_rule_contract(
        subtests,
        rule=mapping_rule(
            min_length=2,
            max_length=3,
            has_key="id",
            has_keys=("name", "role"),
        ),
        valid_values=[
            {"id": 1, "name": "Alice", "role": "admin"},
        ],
        invalid_values=[
            {"id": 1, "name": "Alice"},                 # Missing "role" & fails min_length=2
            {"id": 1, "name": "A", "role": "r", "x": 1}, # Exceeds max_length=3
            {"name": "Alice", "role": "admin"},          # Missing "id"
        ],
        check_raise_invalid=True,
        deep_check=True,
        verbose=False,
    )


def test_mapping_rule_invalid_init_parameters(subtests):
    """Verify that conflicting length parameters raise ParamError."""
    assert_rule_contract(
        subtests,
        rule=mapping_rule(),
        valid_values=[{"a": 1}],
        invalid_values=[123, "not_a_dict", None],
        rule_factory=mapping_rule,
        invalid_init_params=[
            ((), {"length": 2, "min_length": 1}),
        ],
        verbose=False,
    )