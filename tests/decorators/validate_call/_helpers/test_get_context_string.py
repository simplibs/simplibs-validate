import pytest
from simplibs.validate.decorators.validate_call._helpers import get_context_string


def dummy_func():
    pass


class DummyCallableObj:
    pass


def test_get_context_string_standard_function() -> None:
    """Verify context string formatting for standard module functions."""
    result = get_context_string(dummy_func)
    assert result == f"Function {dummy_func.__module__}.{dummy_func.__qualname__}()"


def test_get_context_string_without_module() -> None:
    """Verify fallback formatting when __module__ is missing."""
    func = lambda: None
    object.__setattr__(func, "__module__", None)

    result = get_context_string(func)
    assert result == f"Function {func.__qualname__}()"


def test_get_context_string_fallback_name_with_module() -> None:
    """Verify fallback name 'callable' when name attributes are absent but module exists."""
    obj = DummyCallableObj()

    result = get_context_string(obj)
    assert result == f"Function {obj.__module__}.callable()"


def test_get_context_string_fallback_name_without_module() -> None:
    """Verify full fallback 'Function callable()' when both name attributes and __module__ are absent."""
    obj = DummyCallableObj()
    object.__setattr__(obj, "__module__", None)

    result = get_context_string(obj)
    assert result == "Function callable()"