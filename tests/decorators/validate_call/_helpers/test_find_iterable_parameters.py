import inspect
import typing
from collections.abc import Iterable
from typing import Annotated, Optional

# Tested helper
from simplibs.validate.decorators.validate_call._helpers.find_iterable_parameters import (
    find_iterable_parameters,
)


def _find(func, validated=None) -> tuple[str, ...]:
    """Run the helper on a function; by default every parameter counts as validated."""
    sig = inspect.signature(func)
    names = frozenset(sig.parameters) if validated is None else frozenset(validated)
    return find_iterable_parameters(sig, names)


# ============================================================================
# What is found
# ============================================================================

def test_find_iterable_parameters_plain_iterable_of_t() -> None:
    """Verify Iterable[T] is found."""
    def func(xs: Iterable[int]): ...
    assert _find(func) == ("xs",)


def test_find_iterable_parameters_typing_alias() -> None:
    """Verify typing.Iterable[T] is found as well as collections.abc.Iterable[T]."""
    def func(xs: typing.Iterable[int]): ...
    assert _find(func) == ("xs",)


def test_find_iterable_parameters_union_with_none() -> None:
    """Verify Iterable[T] | None is found."""
    def func(xs: Iterable[int] | None = None): ...
    assert _find(func) == ("xs",)


def test_find_iterable_parameters_optional() -> None:
    """Verify Optional[Iterable[T]] is found."""
    def func(xs: Optional[Iterable[int]] = None): ...
    assert _find(func) == ("xs",)


def test_find_iterable_parameters_annotated() -> None:
    """Verify Annotated[Iterable[T], ...] is found."""
    def func(xs: Annotated[Iterable[int], "meta"]): ...
    assert _find(func) == ("xs",)


def test_find_iterable_parameters_annotated_union() -> None:
    """Verify Annotated wrapping a union with Iterable[T] is found."""
    def func(xs: Annotated[Iterable[int] | None, "meta"] = None): ...
    assert _find(func) == ("xs",)


def test_find_iterable_parameters_keyword_only_and_order() -> None:
    """Verify keyword-only parameters are found and signature order is kept."""
    def func(b: Iterable[int], a: int, *, c: Iterable[str]): ...
    assert _find(func) == ("b", "c")


# ============================================================================
# What is not found
# ============================================================================

def test_find_iterable_parameters_bare_iterable_is_ignored() -> None:
    """Verify bare Iterable is never rejected, so it is never converted."""
    def func(xs: Iterable): ...
    assert _find(func) == ()


def test_find_iterable_parameters_other_collections_are_ignored() -> None:
    """Verify list[T], tuple[T, ...], set[T] and plain types are ignored."""
    def func(a: list[int], b: tuple[int, ...], c: set[int], d: int): ...
    assert _find(func) == ()


def test_find_iterable_parameters_nested_iterable_is_ignored() -> None:
    """Verify Iterable[T] nested inside another annotation is not searched (known limit)."""
    def func(xs: list[Iterable[int]]): ...
    assert _find(func) == ()


def test_find_iterable_parameters_string_annotation_is_ignored() -> None:
    """Verify forward-reference (string) annotations are not resolved (known limit)."""
    def func(xs: "Iterable[int]"): ...
    assert _find(func) == ()


def test_find_iterable_parameters_unannotated_is_ignored() -> None:
    """Verify unannotated parameters are skipped without error."""
    def func(xs, ys=None): ...
    assert _find(func) == ()


def test_find_iterable_parameters_variadic_are_ignored() -> None:
    """Verify `*args` / `**kwargs` are skipped: their annotation describes items, not the collection."""
    def func(*args: Iterable[int], **kwargs: Iterable[int]): ...
    assert _find(func) == ()


def test_find_iterable_parameters_not_validated_is_ignored() -> None:
    """Verify only parameters that have a compiled rule are considered."""
    def func(a: Iterable[int], b: Iterable[int]): ...
    assert _find(func, validated=("b",)) == ("b",)


def test_find_iterable_parameters_bypass_parameter_is_ignored() -> None:
    """Verify the reserved '_validate_call' switch is never reported."""
    def func(xs: Iterable[int], *, _validate_call: bool = True): ...
    assert _find(func) == ("xs",)


def test_find_iterable_parameters_empty_signature() -> None:
    """Verify a function without parameters yields an empty tuple."""
    def func(): ...
    assert _find(func) == ()
