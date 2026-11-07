import pytest

# Tested helper and exceptions
from simplibs.exception import ParamError
from simplibs.validate.decorators.validate_call._validations.raise_no_iterable_parameter import (
    raise_no_iterable_parameter,
)


def sample_func(a: int):
    pass


def test_raise_no_iterable_parameter_raises_param_error() -> None:
    """Verify the helper always raises ParamError."""
    with pytest.raises(ParamError):
        raise_no_iterable_parameter(sample_func)


def test_raise_no_iterable_parameter_error_name() -> None:
    """Verify the raised exception carries the dedicated error name."""
    with pytest.raises(ParamError) as exc_info:
        raise_no_iterable_parameter(sample_func)

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_ITERABLE_PARAM_ERROR"


def test_raise_no_iterable_parameter_works_for_lambdas_and_methods() -> None:
    """Verify any callable with a __qualname__ can be reported."""
    class Holder:
        def method(self, x: int): ...

    for func in (lambda x: x, Holder.method, Holder().method):
        with pytest.raises(ParamError):
            raise_no_iterable_parameter(func)
