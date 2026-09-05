import pytest
# Test tools
from simplibs.exception.testing import assert_exception_class
# Tested classes
from simplibs.validate.exceptions import ValidateError, ValidationError


def test_validation_error_contract(subtests) -> None:
    """Verify that ValidationError meets all class criteria and inherits from ValidateError."""
    assert_exception_class(
        subtests,
        ValidationError,
        expected_parents=ValidateError,
        verbose=False,
        deep_check=True,
    )


def test_validation_error_is_subclass_of_validate_error() -> None:
    """Explicitly confirm catchability via ValidateError."""
    assert issubclass(ValidationError, ValidateError)