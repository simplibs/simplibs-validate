import inspect
from typing import Any


def resolve_parameter_annotation(param: inspect.Parameter) -> Any:
    """Return the annotation that describes the value the function body sees.

    For a variadic parameter, Python's annotation describes each *element*,
    while the bound value is the whole collection:

        *args: int     -> the body sees tuple[int, ...]
        **kwargs: int  -> the body sees dict[str, int]

    Every other parameter kind keeps its annotation unchanged.

    Args:
        param: The parameter whose annotation is resolved. Must be annotated.

    Returns:
        The annotation to hand to build_typing_rule.
    """

    # 1. *args — the annotation describes every positional item
    if param.kind is inspect.Parameter.VAR_POSITIONAL:
        return tuple[param.annotation, ...]

    # 2. **kwargs — the annotation describes every keyword value
    if param.kind is inspect.Parameter.VAR_KEYWORD:
        return dict[str, param.annotation]

    # 3. Regular parameter — annotation is already about the bound value
    return param.annotation


_DESIGN_NOTES = """
# resolve_parameter_annotation — Variadic Parameter Annotation Resolver

## Purpose
Translates what a variadic parameter's annotation *means* in Python into
what validate_call actually receives. `*args: X` annotates each item, but
`bound.arguments` holds one tuple; `**kwargs: X` annotates each value, but
`bound.arguments` holds one dict. Without this step the rule built from `X`
was applied to the whole collection and failed.

---

## 1. Why a Synthesized Annotation and Not a New Rule

The result is handed to build_typing_rule like any other annotation, so
`tuple[X, ...]` and `dict[str, X]` reuse the existing, tested builders
(type check + ForEach over items / over values). No new rule, no change in
the rules library, and error messages come from code that already exists.

---

## 2. Overrides Apply to the Whole Collection

An override is combined with this rule through AllOf in
compile_parameter_rules, so it sees exactly what the function body sees
(the tuple or dict). That makes collection-level rules possible
(`HasLength(min_length=1)` on `*args`); an item-level rule is written as
`ForEach(...)` inside the override.

---

## 3. Bare and Unsubscripted Cases

`*args: tuple` or `**kw: dict` are not special: they simply mean
`tuple[tuple, ...]` / `dict[str, dict]`, i.e. the items themselves are
tuples / dicts — the Python meaning of the annotation, unchanged.
"""
