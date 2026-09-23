import pytest
from typing import Callable, Any

# Tested function
from simplibs.validate.decorators.log_this._helpers.unwrap_log_this import (
    unwrap_log_this,
)


def base_function() -> str:
    return "original"


def test_unwrap_log_this_no_wrapper() -> None:
    """Verify that an unwrapped function is returned as-is."""
    assert unwrap_log_this(base_function) is base_function


def test_unwrap_log_this_single_layer() -> None:
    """Verify peeling off a single log_this layer via __wrapped__."""
    def wrapper():
        pass

    wrapper._is_log_this_wrapper = True
    wrapper.__wrapped__ = base_function

    assert unwrap_log_this(wrapper) is base_function


def test_unwrap_log_this_multiple_layers() -> None:
    """Verify peeling off multiple nested log_this layers."""
    def inner_wrapper():
        pass
    inner_wrapper._is_log_this_wrapper = True
    inner_wrapper.__wrapped__ = base_function

    def outer_wrapper():
        pass
    outer_wrapper._is_log_this_wrapper = True
    outer_wrapper.__wrapped__ = inner_wrapper

    assert unwrap_log_this(outer_wrapper) is base_function


def test_unwrap_log_this_stops_at_foreign_wrapper() -> None:
    """Verify unwrapping stops when encountering a wrapper without the log_this marker."""
    def standard_decorator():
        pass
    # Foreign decorator without _is_log_this_wrapper attribute
    standard_decorator.__wrapped__ = base_function

    def log_wrapper():
        pass
    log_wrapper._is_log_this_wrapper = True
    log_wrapper.__wrapped__ = standard_decorator

    # Unwrapping must stop at 'standard_decorator' and preserve it
    assert unwrap_log_this(log_wrapper) is standard_decorator


def test_unwrap_log_this_missing_wrapped_attribute_safely_breaks() -> None:
    """Verify loop terminates safely if marker is True but __wrapped__ attribute is missing."""
    def broken_wrapper():
        pass

    broken_wrapper._is_log_this_wrapper = True
    # Intentionally missing __wrapped__ attribute

    # Should safely terminate loop and return the wrapper itself
    assert unwrap_log_this(broken_wrapper) is broken_wrapper