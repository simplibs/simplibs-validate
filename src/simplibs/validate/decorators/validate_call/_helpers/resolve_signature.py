import inspect
import typing
from typing import Any, Callable
# Outers
from .._validations import raise_unresolvable_annotation
# Inners
from .needs_annotation_resolution import needs_annotation_resolution


def resolve_signature(
    func: Callable[..., Any],
    *,
    strict: bool = False,
) -> inspect.Signature | None:
    """Return the function's signature with string annotations evaluated.

    Only annotations that really contain an unresolved name are replaced;
    every other annotation (and a signature without any) is returned exactly
    as `inspect.signature` gives it.

    Args:
        func: The function (or dataclass __init__) to inspect.
        strict: If False, a name that does not exist yet yields None, so the
            caller can try again later. If True, it raises.

    Returns:
        The resolved signature, or None when `strict` is False and a name is
        not defined yet.

    Raises:
        ParamError: If an annotation cannot be evaluated for any reason other
            than a missing name, or for a missing name when `strict` is True.
    """

    signature = inspect.signature(func)
    empty = inspect.Parameter.empty

    # 1. Which annotations still contain a name?
    names = [
        param.name
        for param in signature.parameters.values()
        if param.annotation is not empty and needs_annotation_resolution(param.annotation)
    ]
    return_needs = (
        signature.return_annotation is not inspect.Signature.empty
        and needs_annotation_resolution(signature.return_annotation)
    )

    # 2. Nothing to resolve — behave exactly as before
    if not names and not return_needs:
        return signature

    # 3. Evaluate, including references nested in generics
    try:
        hints = typing.get_type_hints(func, include_extras=True)
    except NameError as error:
        if strict:
            raise_unresolvable_annotation(func, error)
        return None
    except Exception as error:
        raise_unresolvable_annotation(func, error)

    # 4. Replace only what needed resolving
    parameters = [
        param.replace(annotation=hints.get(param.name, param.annotation))
        if param.name in names else param
        for param in signature.parameters.values()
    ]
    return signature.replace(
        parameters=parameters,
        return_annotation=hints.get("return", signature.return_annotation) if return_needs else signature.return_annotation,
    )


_DESIGN_NOTES = """
# resolve_signature — Signature With Evaluated String Annotations

## Purpose
Turns `"int"`, `list["Node"]` or a whole `from __future__ import annotations`
module into annotations build_typing_rule can decompose. Uses
`typing.get_type_hints(include_extras=True)`, which also resolves references
*nested* inside generics and keeps `Annotated` metadata.

---

## 1. Replace Only What Needed Resolving

get_type_hints normalises more than strings (for instance `None` becomes
`NoneType`). Annotations that were already real objects are therefore taken
from the original signature untouched, so existing code sees no difference.

---

## 2. Two Failure Modes

* **A name that does not exist (yet)** — `NameError`. Common and often
  temporary: a method annotated with its own class, or a class defined further
  down the module. With `strict=False` this returns None and the caller retries
  at the first call; with `strict=True` it raises.
* **Anything else** (invalid syntax, a failing expression) — never going to
  work later, so it raises immediately.

---

## 3. Limits

Names are looked up in the module of the function. A class defined inside
another function, or a name imported only under TYPE_CHECKING, cannot be found
and is reported by raise_unresolvable_annotation.
"""
