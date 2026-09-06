import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.validate.exceptions import ParamError
from simplibs.validate.tools.override_rules._validations import (
    raise_override_rules_invalid_error,
)


@pytest.mark.parametrize(
    "name, rule",
    [
        ("age", 123),
        ("email", "not_a_rule"),
        ("items", None),
        ("status", [1, 2, 3]),
    ],
)
def test_raise_override_rules_invalid_error_contract(
    subtests,
    name,
    rule,
) -> None:
    """Verify that raise_override_rules_invalid_error raises ParamError wrapping ValueError for invalid override rule values."""

    assert_exception_function(
        subtests,
        raise_override_rules_invalid_error,
        invalid_params=(name, rule),
        exception_type=ParamError,
        error_name="OVERRIDE_RULES_INVALID_ERROR",
        label=name,
        expected="a Rule instance or a callable predicate",
        value=rule,
        problem=(
            f"The value supplied for parameter '{name}' is invalid.",
            f"Received {rule!r}, which is neither a Rule instance nor a callable.",
        ),
        how_to_fix=(
            f"Provide a valid Rule instance or callable predicate for '{name}'.",
            "Example with Rule: override_rules(age=greater_than(0))",
            "Example with callable: override_rules(age=lambda v: v > 0)",
        ),
        exception=ValueError,
        verbose=False,
    )