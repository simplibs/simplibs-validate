import pytest

from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.validate.tools._validations import (
    raise_validated_type_rule_invalid_error,
)


@pytest.mark.parametrize(
    "rule, index",
    [
        (123, 0),
        ("not_a_rule", 1),
        (None, 2),
        ([1, 2, 3], 0),
    ],
)
def test_raise_validated_type_rule_invalid_error_contract(
    subtests,
    rule,
    index,
) -> None:
    """Verify that raise_validated_type_rule_invalid_error raises ParamError
    wrapping ValueError when a non-rule argument is passed to validated_type()."""

    assert_exception_function(
        subtests,
        raise_validated_type_rule_invalid_error,
        invalid_params=(rule, index),
        exception_type=ParamError,
        error_name="VALIDATED_TYPE_RULE_INVALID_ERROR",
        label="rules",
        expected="a Rule instance or a callable predicate",
        value=rule,
        problem=(
            f"The rule at position {index} in validated_type() is invalid.",
            f"Received {rule!r}, which is neither a Rule instance nor a callable.",
        ),
        how_to_fix=(
            "Provide a valid Rule instance or callable predicate at every position.",
            "Example with Rule: validated_type(int, greater_than(0))",
            "Example with callable: validated_type(int, lambda v: v > 0)",
        ),
        exception=ValueError,
        verbose=False,
    )