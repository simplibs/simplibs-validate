import pytest
from simplibs.validate.tools.log_this._helpers import get_context_info


def sample_function() -> None:
    pass


class CallableObject:
    def __call__(self) -> None:
        pass


def test_get_context_info_standard_function() -> None:
    """Verify metadata extraction for standard functions."""
    info = get_context_info(sample_function)
    assert info["name"] == sample_function.__qualname__
    assert info["module"] == sample_function.__module__


def test_get_context_info_lambda() -> None:
    """Verify metadata extraction for lambda functions."""
    lambda_fn = lambda x: x
    info = get_context_info(lambda_fn)
    assert "<lambda>" in info["name"]
    assert info["module"] == sample_fn.__module__ if (sample_fn := lambda_fn) else True


def test_get_context_info_callable_object_without_attributes() -> None:
    """Verify fallback name 'callable' when callable object lacks __qualname__ and __name__."""
    obj = CallableObject()
    info = get_context_info(obj)
    assert info["name"] == "callable"
    assert info["module"] == obj.__module__


def test_get_context_info_missing_module() -> None:
    """Verify module returns None when __module__ is missing."""
    func = lambda: None
    object.__setattr__(func, "__module__", None)

    info = get_context_info(func)
    assert info["module"] is None