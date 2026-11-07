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


def test_string_rule_exact_length(subtests):
    """Verify length alone requires exactly that many characters."""
    assert_rule_contract(
        subtests,
        rule=string_rule(length=3),
        valid_values=["abc", "   "],
        invalid_values=["ab", "abcd", "", 123],
        deep_check=True,
        verbose=False,
    )


def test_string_rule_is_substring_of(subtests):
    """Verify is_substring_of requires the value to occur inside the given string."""
    assert_rule_contract(
        subtests,
        rule=string_rule(is_substring_of="hello world"),
        valid_values=["hello", "world", "o w"],
        invalid_values=["goodbye", "hello world!", 123],
        deep_check=True,
        verbose=False,
    )


def test_string_rule_equals(subtests):
    """Verify equals is an exact, case-sensitive match."""
    assert_rule_contract(
        subtests,
        rule=string_rule(equals="abc"),
        valid_values=["abc"],
        invalid_values=["abd", "ABC", ""],
        deep_check=True,
        verbose=False,
    )


def test_string_rule_not_equals(subtests):
    """Verify not_equals rejects only the exact string."""
    assert_rule_contract(
        subtests,
        rule=string_rule(not_equals="abc"),
        valid_values=["abd", "ABC", ""],
        invalid_values=["abc"],
        deep_check=True,
        verbose=False,
    )


def test_string_rule_is_in(subtests):
    """Verify is_in accepts only the listed strings."""
    assert_rule_contract(
        subtests,
        rule=string_rule(is_in={"a", "b"}),
        valid_values=["a", "b"],
        invalid_values=["c", ""],
        deep_check=True,
        verbose=False,
    )


def test_string_rule_not_in(subtests):
    """Verify not_in rejects the listed strings."""
    assert_rule_contract(
        subtests,
        rule=string_rule(not_in={"a", "b"}),
        valid_values=["c", ""],
        invalid_values=["a", "b"],
        deep_check=True,
        verbose=False,
    )
