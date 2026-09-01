import pytest
# Test tools
from simplibs.exception.testing import assert_exception_class
# Tested class
from simplibs.validate.exceptions import ValidateError


def test_validate_error_contract(subtests) -> None:
    """Verify that ValidateError satisfies inheritance, defaults, constructor,
    and public API checks.
    """
    assert_exception_class(
        subtests,
        ValidateError,
        verbose=False,
        deep_check=True,
    )


def test_validate_error_skip_locations() -> None:
    """Verify that skip_locations points to 'simplibs/validate'."""
    err = ValidateError(message="Validation failed")
    assert "simplibs/validate" in err.skip_locations