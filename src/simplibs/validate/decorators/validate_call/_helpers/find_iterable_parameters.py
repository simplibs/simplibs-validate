import inspect
import types
from collections.abc import Iterable
from typing import Annotated, Any, Union, get_args, get_origin
# Inners
from .is_bypass_parameter import is_bypass_parameter


def _is_iterable_of(annotation: Any) -> bool:
    """True if the annotation is Iterable[T] (directly, in a union, or in Annotated)."""

    origin = get_origin(annotation)

    # 1. Annotated[X, ...] — look at the wrapped type only
    if origin is Annotated:
        return _is_iterable_of(get_args(annotation)[0])

    # 2. X | Y / Union[X, Y] — any member being Iterable[T] is enough
    if origin is Union or origin is types.UnionType:
        return any(_is_iterable_of(member) for member in get_args(annotation))

    # 3. Iterable[T] itself — bare Iterable has no args and is never rejected
    return origin is Iterable and bool(get_args(annotation))


def find_iterable_parameters(
    signature: inspect.Signature,
    validated: frozenset[str] | set[str],
) -> tuple[str, ...]:
    """Names of validated parameters annotated as Iterable[T].

    These are exactly the parameters for which build_typing_rule rejects
    one-shot iterators, i.e. the only ones where materializing an iterator
    changes an outcome from "rejected" to "accepted".

    Args:
        signature: The decorated function's inspect.Signature.
        validated: Names of parameters that have a compiled rule.

    Returns:
        Parameter names in signature order. Variadic parameters
        (`*args`, `**kwargs`) are never included.
    """

    names: list[str] = []
    for name, param in signature.parameters.items():

        # 1. Only parameters that are actually validated
        if name not in validated or is_bypass_parameter(param):
            continue

        # 2. Variadic parameters annotate their items, not the bound collection
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        # 3. Annotation must be Iterable[T]
        if param.annotation is not inspect.Parameter.empty and _is_iterable_of(param.annotation):
            names.append(name)

    return tuple(names)


_DESIGN_NOTES = """
# find_iterable_parameters — Decoration-Time Detector of Iterable[T] Parameters

## Purpose
Finds, once at decoration time, the parameters for which
`materialize_iterators=True` has any effect: validated parameters whose
annotation is `Iterable[T]` — directly, as a member of a union
(`Iterable[int] | None`), or inside `Annotated[...]`.

---

## 1. Why Only Iterable[T]

`Iterable[T]` is the single annotation for which build_typing_rule rejects a
one-shot iterator (IsReiterable). Materializing there turns a rejection into
an accepted, explicitly requested conversion. A bare `Iterable`, `Any` or
`object` is never rejected, so the function may legitimately want the lazy
iterator (streaming) — converting it would silently change behavior, which is
exactly what the flag must not do.

---

## 2. Known Limits

* Nested annotations (`list[Iterable[int]]`) are not searched.
* Variadic parameters are skipped: their annotation describes items, not the
  bound tuple/dict.
* A string (forward-reference) annotation is not resolved and is not matched.
"""
