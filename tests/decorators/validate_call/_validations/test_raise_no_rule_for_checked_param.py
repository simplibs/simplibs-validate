import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.validate.decorators.validate_call._validations import (
    raise_no_rule_for_checked_param,
)


def sample_function(x, y):
    pass


@pytest.mark.parametrize(
    "func, param_name",
    [
        (sample_function, "x"),
        (sample_function, "y"),
    ],
)
def test_raise_no_rule_for_checked_param_contract(subtests, func, param_name) -> None:
    """Verify raise_no_rule_for_checked_param produces a well-formed ParamError card."""

    def raising_wrapper(target_func, name):
        raise_no_rule_for_checked_param(target_func, name)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(func, param_name),
        exception_type=ParamError,
        error_name="VALIDATE_CALL_NO_RULE_FOR_PARAM_ERROR",
        label="check",
        expected="A parameter with a type annotation or an entry in overrides.",
        value=param_name,
        problem=(
            f"Parameter '{param_name}' of {func.__qualname__}() was listed in 'check'.",
            "The parameter has neither a type annotation nor a custom override rule.",
        ),
        how_to_fix=(
            f"Add a type annotation to parameter '{param_name}'.",
            f"Provide an explicit rule entry: overrides={{'{param_name}': ...}}.",
            f"Remove '{param_name}' from the 'check' parameter list.",
        ),
        verbose=False,
    )