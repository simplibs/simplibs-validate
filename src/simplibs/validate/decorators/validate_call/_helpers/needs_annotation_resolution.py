from typing import Annotated, Any, ForwardRef, Literal, get_args, get_origin


def needs_annotation_resolution(annotation: Any) -> bool:
    """Tell whether an annotation still contains an unresolved name.

    True for a string (`"int"`, produced by `from __future__ import
    annotations` or written by hand) and for a ForwardRef, also when nested
    inside a generic (`list["Node"]`, `Optional["Node"]`, `Callable[["A"], "B"]`).

    Two places where a `str` is *not* a reference are skipped on purpose:
    the values of `Literal[...]` and the metadata of `Annotated[T, ...]`.

    Args:
        annotation: Any annotation object, including a Rule instance used directly.

    Returns:
        True if resolving the annotation would change it, otherwise False.
    """

    # 1. A name that still has to be evaluated
    if isinstance(annotation, (str, ForwardRef)):
        return True

    # 2. Argument lists of Callable[[A, B], R] arrive as a plain list
    if isinstance(annotation, (list, tuple)):
        return any(needs_annotation_resolution(item) for item in annotation)

    origin = get_origin(annotation)

    # 3. Literal["a", "b"] holds values, not references
    if origin is Literal:
        return False

    # 4. Annotated[T, meta...] — only T is a type, the rest is free-form metadata
    if origin is Annotated:
        return needs_annotation_resolution(get_args(annotation)[0])

    # 5. Any other generic — look at its arguments
    return any(needs_annotation_resolution(arg) for arg in get_args(annotation))


_DESIGN_NOTES = """
# needs_annotation_resolution — Detector of Unresolved Names in an Annotation

## Purpose
Decides whether a signature has to be resolved at all. Annotations that are
already real objects are left exactly as they are, so code that never used
string annotations behaves the same as before this helper existed.

---

## 1. Strings That Are Not References

`Literal["a", "b"]` stores string *values* and `Annotated[int, "text"]`
stores free-form metadata. Treating them as unresolved names would send
perfectly valid annotations through evaluation and fail on them, so both are
skipped explicitly.

---

## 2. Nested References

`from __future__ import annotations` turns the whole annotation into one
string, but a reference can also sit inside a real generic written by hand
(`list["Node"]`). Both are detected, including the argument list of
`Callable[["A"], "B"]`, which typing exposes as a plain list.
"""
