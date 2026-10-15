import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.validate.decorators.log_this._validations import raise_invalid_max_items


@pytest.mark.parametrize("max_items", [0, -5, True, "10", 2.5])
def test_raise_invalid_max_items_contract(subtests, max_items) -> None:
    """Verify raise_invalid_max_items produces a well-formed ParamError card."""

    assert_exception_function(
        subtests,
        raise_invalid_max_items,
        invalid_params=(max_items,),
        exception_type=ParamError,
        error_name="LOG_THIS_INVALID_MAX_ITEMS_ERROR",
        label="max_items",
        expected="None (no shortening) or a positive integer.",
        value=max_items,
        problem=(
            f"Option 'max_items={max_items!r}' of log_this() is not valid.",
            "It must be None or a positive integer: the number of items shown per container.",
        ),
        how_to_fix=(
            "Pass a positive integer, e.g. max_items=10.",
            "Pass max_items=None to log arguments and results in full.",
        ),
        verbose=False,
    )
