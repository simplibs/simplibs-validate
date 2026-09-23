"""Tests for the string_rule composition factory."""

from simplibs.rules.testing import assert_rule_contract
from simplibs.validate.validators.rules import string_rule


def test_string_rule_default_contract(subtests):
    """Verify default string_rule (acts purely as is_string check)."""
    assert_rule_contract(
        subtests,
        rule=string_rule(),
        valid_values=["hello", "", "123"],
        invalid_values=[123, 45.6, True, None, ["a"]],
        rule_factory=string_rule,
        deep_check=True,
        verbose=False,
    )


def test_string_rule_combined_constraints(subtests):
    """Verify string_rule with string-specific matching, regex, and blankness."""
    assert_rule_contract(
        subtests,
        rule=string_rule(
            min_length=5,
            max_length=15,
            starts_with="user_",
            ends_with="_sys",
            contains="admin",
            regex_search=r"^\w+$",
            is_blank=False,
        ),
        valid_values=["user_admin_sys"],
        invalid_values=[
            "user_sys",          # Missing "admin"
            "user_admin_sys!",   # Fails regex (\w+)
            "usr_admin_sys",     # Fails starts_with
            "user_admin_xyz",     # Fails ends_with
            "user_admin_system_sys", # Exceeds max_length
        ],
        deep_check=True,
        verbose=False,
    )


def test_string_rule_is_blank_tristate(subtests):
    """Verify tri-state behavior of is_blank parameter."""
    # Must be blank
    assert_rule_contract(
        subtests,
        rule=string_rule(is_blank=True),
        valid_values=["", "   ", "\t\n"],
        invalid_values=["a", "  a  "],
        deep_check=True,
        verbose=False,
    )

    # Must NOT be blank
    assert_rule_contract(
        subtests,
        rule=string_rule(is_blank=False),
        valid_values=["a", "  a  "],
        invalid_values=["", "   ", "\t\n"],
        deep_check=True,
        verbose=False,
    )


def test_string_rule_invalid_init_parameters(subtests):
    """Verify that conflicting length parameters raise ParamError."""
    assert_rule_contract(
        subtests,
        rule=string_rule(),
        valid_values=["a"],
        invalid_values=[123, None, True],
        rule_factory=string_rule,
        invalid_init_params=[
            ((), {"length": 5, "min_length": 3}),
        ],
        verbose=False,
    )