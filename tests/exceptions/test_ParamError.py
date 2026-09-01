import pytest
# Test tools
from simplibs.exception.testing import assert_exception_class
# Tested classes
from simplibs.validate.exceptions import ParamError, ValidateError


def test_param_error_contract(subtests) -> None:
    """Verify that ParamError meets all class criteria and inherits from ValidateError."""
    assert_exception_class(
        subtests,
        ParamError,
        expected_parents=ValidateError,
        verbose=False,
        deep_check=True,
    )


def test_param_error_is_subclass_of_validate_error() -> None:
    """Explicitly confirm catchability via ValidateError."""
    assert issubclass(ParamError, ValidateError)