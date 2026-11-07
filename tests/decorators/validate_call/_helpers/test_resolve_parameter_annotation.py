import inspect

import pytest

# Tested helper
from simplibs.validate.decorators.validate_call._helpers.resolve_parameter_annotation import (
    resolve_parameter_annotation,
)


def _param(func, name: str) -> inspect.Parameter:
    """Return one parameter of the given function."""
    return inspect.signature(func).parameters[name]


def regular(a: int, b: int | str, /, c: float, *, d: list[int]): ...
def variadic(*args: int, **kwargs: str): ...
def variadic_union(*args: int | str, **kwargs: int | None): ...
def variadic_generic(*args: list[int], **kwargs: dict[str, int]): ...


# ============================================================================
# Regular parameters stay untouched
# ============================================================================

@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("a", int),            # positional-only
        ("b", int | str),      # positional-only, union
        ("c", float),          # positional-or-keyword
        ("d", list[int]),      # keyword-only
    ],
)
def test_resolve_parameter_annotation_regular_parameter_is_unchanged(name, expected) -> None:
    """Verify non-variadic parameters keep their annotation exactly."""
    assert resolve_parameter_annotation(_param(regular, name)) == expected


# ============================================================================
# Variadic parameters
# ============================================================================

def test_resolve_parameter_annotation_var_positional() -> None:
    """Verify `*args: int` resolves to tuple[int, ...]."""
    assert resolve_parameter_annotation(_param(variadic, "args")) == tuple[int, ...]


def test_resolve_parameter_annotation_var_keyword() -> None:
    """Verify `**kwargs: str` resolves to dict[str, str]."""
    assert resolve_parameter_annotation(_param(variadic, "kwargs")) == dict[str, str]


def test_resolve_parameter_annotation_var_positional_union() -> None:
    """Verify a union annotation is kept whole inside the tuple."""
    assert resolve_parameter_annotation(_param(variadic_union, "args")) == tuple[int | str, ...]


def test_resolve_parameter_annotation_var_keyword_union() -> None:
    """Verify a union annotation is kept whole inside the dict."""
    assert resolve_parameter_annotation(_param(variadic_union, "kwargs")) == dict[str, int | None]


def test_resolve_parameter_annotation_var_positional_generic_item() -> None:
    """Verify a generic item annotation is nested, not flattened."""
    assert resolve_parameter_annotation(_param(variadic_generic, "args")) == tuple[list[int], ...]


def test_resolve_parameter_annotation_var_keyword_generic_item() -> None:
    """Verify a generic value annotation is nested, not flattened."""
    assert resolve_parameter_annotation(_param(variadic_generic, "kwargs")) == dict[str, dict[str, int]]
