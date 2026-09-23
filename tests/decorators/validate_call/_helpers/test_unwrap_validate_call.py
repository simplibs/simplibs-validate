import pytest
from typing import Callable, Any

# Testovaná funkce
from simplibs.validate.decorators.validate_call._helpers.unwrap_validate_call import (
    unwrap_validate_call,
)


def base_function() -> str:
    return "original"


def test_unwrap_validate_call_no_wrapper() -> None:
    """Verify that an unwrapped function is returned as-is."""
    assert unwrap_validate_call(base_function) is base_function


def test_unwrap_validate_call_single_layer() -> None:
    """Verify peeling off a single validate_call layer via __wrapped__."""

    def wrapper():
        pass

    wrapper._is_validate_call_wrapper = True
    wrapper.__wrapped__ = base_function

    assert unwrap_validate_call(wrapper) is base_function


def test_unwrap_validate_call_multiple_layers() -> None:
    """Verify peeling off multiple nested validate_call layers."""

    def inner_wrapper():
        pass

    inner_wrapper._is_validate_call_wrapper = True
    inner_wrapper.__wrapped__ = base_function

    def outer_wrapper():
        pass

    outer_wrapper._is_validate_call_wrapper = True
    outer_wrapper.__wrapped__ = inner_wrapper

    assert unwrap_validate_call(outer_wrapper) is base_function


def test_unwrap_validate_call_stops_at_foreign_wrapper() -> None:
    """Verify unwrapping stops when encountering a wrapper without the marker."""

    def standard_decorator():
        pass

    # Běžný dekorátor bez markeru _is_validate_call_wrapper
    standard_decorator.__wrapped__ = base_function

    def validate_wrapper():
        pass

    validate_wrapper._is_validate_call_wrapper = True
    validate_wrapper.__wrapped__ = standard_decorator

    # Musí se odbalit pouze 'validate_wrapper', 'standard_decorator' se zachová
    assert unwrap_validate_call(validate_wrapper) is standard_decorator


def test_unwrap_validate_call_fallback_to_func() -> None:
    """Verify fallback to __func__ if __wrapped__ is not present."""

    def method_wrapper():
        pass

    method_wrapper._is_validate_call_wrapper = True
    method_wrapper.__func__ = base_function

    assert unwrap_validate_call(method_wrapper) is base_function


def test_unwrap_validate_call_missing_both_attributes_safely_breaks() -> None:
    """Verify loop terminates safely if marker is True but structural attributes are missing."""

    def broken_wrapper():
        pass

    broken_wrapper._is_validate_call_wrapper = True
    # Záměrně chybí __wrapped__ i __func__

    # Očekáváme bezpečné přerušení cyklu a vrácení samotného (nekompletního) wrapperu
    assert unwrap_validate_call(broken_wrapper) is broken_wrapper