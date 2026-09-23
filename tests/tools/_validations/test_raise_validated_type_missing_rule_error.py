import pytest

from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.validate.tools._validations import (
    raise_validated_type_missing_rule_error,
)


@pytest.mark.parametrize(
    "type_",
    [
        int,
        str,
        float,
        dict,
    ],
)
def test_raise_validated_type_missing_rule_error_contract(
    subtests,
    type_,
) -> None:
    """Verify that raise_validated_type_missing_rule_error raises ParamError
    wrapping ValueError when validated_type() is called without rules."""
    type_name = getattr(type_, "__name__", repr(type_))

    assert_exception_function(
        subtests,
        raise_validated_type_missing_rule_error,
        invalid_params=(type_,),
        exception_type=ParamError,
        error_name="VALIDATED_TYPE_MISSING_RULE_ERROR",
        label="rules",
        expected="at least one Rule instance or callable predicate",
        value=type_,
        problem=(
            f"validated_type({type_!r}) was called with zero validation rules.",
            "At least one rule or callable predicate is required.",
        ),
        how_to_fix=(
            f"Pass at least one rule, e.g. validated_type({type_name}, greater_than(0)).",
            f"If no constraint is needed, use '{type_name}' directly as the annotation.",
        ),
        exception=ValueError,
        verbose=False,
    )