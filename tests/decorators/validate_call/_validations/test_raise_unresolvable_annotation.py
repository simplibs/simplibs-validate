import pytest

# Tested helper and exceptions
from simplibs.exception import ParamError
from simplibs.validate.decorators.validate_call._validations.raise_unresolvable_annotation import (
    raise_unresolvable_annotation,
)


def sample_func(a: "Missing"):
    pass


def test_raise_unresolvable_annotation_raises_param_error() -> None:
    """Verify the helper always raises ParamError."""
    with pytest.raises(ParamError):
        raise_unresolvable_annotation(sample_func, NameError("name 'Missing' is not defined"))


def test_raise_unresolvable_annotation_error_name() -> None:
    """Verify the raised exception carries the dedicated error name."""
    with pytest.raises(ParamError) as exc_info:
        raise_unresolvable_annotation(sample_func, NameError("x"))

    assert exc_info.value.error_name == "VALIDATE_CALL_UNRESOLVABLE_ANNOTATION_ERROR"


def test_raise_unresolvable_annotation_keeps_original_error_as_cause() -> None:
    """Verify the evaluation error stays attached for the traceback."""
    original = NameError("name 'Missing' is not defined")

    with pytest.raises(ParamError) as exc_info:
        raise_unresolvable_annotation(sample_func, original)

    assert exc_info.value.__cause__ is original


def test_raise_unresolvable_annotation_works_for_any_exception_type() -> None:
    """Verify non-NameError failures (for example invalid syntax) are reported too."""
    with pytest.raises(ParamError):
        raise_unresolvable_annotation(sample_func, SyntaxError("invalid syntax"))
