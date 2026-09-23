import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.validate.decorators.validate_call._validations import (
    raise_no_rule_for_return,
)


def dummy_function():
    pass


def another_function(a, b):
    pass


@pytest.mark.parametrize(
    "func",
    [
        dummy_function,
        another_function,
    ],
)
def test_raise_no_rule_for_return_contract(subtests, func) -> None:
    """Verify raise_no_rule_for_return produces a well-formed ParamError card."""

    def raising_wrapper(target_func):
        raise_no_rule_for_return(target_func)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(func,),
        exception_type=ParamError,
        error_name="VALIDATE_CALL_NO_RULE_FOR_RETURN_ERROR",
        label="check_return",
        expected="A function with an explicit return type annotation.",
        value=func.__qualname__,
        problem=(
            f"Option 'check_return=True' was enabled for function {func.__qualname__}().",
            "The function does not define a return type annotation ('-> ...') to validate against.",
        ),
        how_to_fix=(
            f"Add a return type annotation to function {func.__qualname__}().",
            "Disable return validation by removing 'check_return=True'.",
        ),
        verbose=False,
    )