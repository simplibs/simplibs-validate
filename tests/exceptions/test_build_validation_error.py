import pytest
# Test tools
from simplibs.exception.testing import assert_exception_function
# Tested function and exception
from simplibs.validate.exceptions import ValidateError, build_validation_error


def is_even(x: int) -> bool:
    return x % 2 == 0


@pytest.mark.parametrize(
    "rule, rule_name",
    [
        (is_even, "is_even"),
        (lambda x: x > 0, "<lambda>"),
    ],
)
def test_build_validation_error_contract(subtests, rule, rule_name) -> None:
    """Verify build_validation_error contract by wrapping it into a raising lambda."""
    value = "invalid_value"
    value_name = "test_param"
    context = "user_input_check"

    def raising_wrapper(*args):
        raise build_validation_error(*args)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(rule, value, value_name, context),
        exception_type=ValidateError,
        error_name="VALIDATION_ERROR",
        label=value_name,
        expected=f"value satisfying callable condition '{rule_name}'",
        value=value,
        problem=f"Value failed validation check executed by callable '{rule_name}'.",
        context=context,
        how_to_fix=(
            f"Provide a value that evaluates to True when passed to '{rule_name}'.",
        ),
        exception=ValueError,
        verbose=False,
    )