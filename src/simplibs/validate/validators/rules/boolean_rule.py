from simplibs.rules import (
    Rule,
    AllOf,
    is_bool as _is_bool,
    equals as _equals,
)


def boolean_rule(
    *,
    equals: bool | None = None,
) -> Rule:
    """Compose a Rule validating a boolean against the given optional constraints.

    Args:
        equals: If given, the value must equal this exact boolean (True or False).

    Returns:
        A single Rule instance — `is_bool` itself if no constraint is
        given, otherwise an AllOf combining the type check with the
        constraint.
    """
    # 1. Base type check
    parts: list[Rule] = [_is_bool]

    # 2. Exact equality
    if equals is not None:
        parts.append(_equals(equals))

    # 3. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# boolean_rule — Composed Boolean Validation Rule

## Purpose
Layer-3 composition over `IsBool` (layer 1) / `is_bool` (layer 2). Kept
deliberately minimal — booleans have essentially one meaningful optional
constraint (an exact expected value) beyond their type.

---

## 1. Design Pattern (shared across every `*_rule.py` / `validate_*.py` pair)

* **`<type>_rule(...) -> Rule`:** Builds and returns a `Rule` instance
  from the given optional constraints — never validates anything itself.
  Build once, reuse many times (`validate()`, `.validate()`, or further
  composition with `|`/`&`/`~`).
* **`validate_<type>(value, ...) -> Any`:** A thin convenience wrapper —
  `return <type>_rule(...).validate(value, ...)`. No logic is duplicated
  between the two.
* **`None` as the "Not Given" Sentinel:** Every optional constraint
  parameter defaults to plain `None`, safe everywhere `None` can never be
  a legitimate constrained value itself (a length, a threshold, a class,
  a prefix, ...). The one documented exception in this package is
  `mapping_rule`'s `has_key`, which uses `UNSET` because `None` is itself
  a valid dict key.
* **Zero-Overhead Empty Case:** When no optional constraints are given,
  `parts` contains only the base type rule and `<type>_rule()` returns it
  directly — no `AllOf` wrapper is constructed.
* **Private Shortcut Aliases:** Every layer-2 shortcut used to build
  `parts` is imported under a leading-underscore alias (`is_bool as
  _is_bool`, `equals as _equals`, ...), freeing the public parameter names
  from needing a trailing underscore to avoid shadowing.
* **Top-Level `AllOf` Import:** Imported directly at module level —
  `..rules` already imports it at its own top level regardless, so a
  lazy, function-local import buys no circularity protection here.

---

## 2. Hot-Loop Guidance

`validate_bool(value, equals=True)` called inside a large loop rebuilds
`Equals(True)` and its containing rule on every iteration. For repeated
validation against the same fixed constraints, prefer:

    rule = boolean_rule(equals=True)
    for value in many_values:
        rule.validate(value)

over calling `validate_bool(value, equals=True)` per iteration.
"""