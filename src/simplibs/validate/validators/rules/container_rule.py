from typing import Any, Callable, Collection
from simplibs.rules import (
    Rule,
    AllOf,
    ForEach,
    is_container as _is_container,
    has_length as _has_length,
    all_unique as _all_unique,
    has_item as _has_item,
    is_subset_of as _is_subset_of,
    is_superset_of as _is_superset_of,
)


def container_rule(
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    unique: bool = False,
    has_item: Any | None = None,
    subset_of: Collection[Any] | None = None,
    superset_of: Collection[Any] | None = None,
    for_each: Rule | Callable[[Any], bool] | None = None,
) -> Rule:
    """Compose a Rule validating a container against the given optional constraints.

    Args:
        min_length: Minimum allowed number of items. Ignored if `length` is also given.
        max_length: Maximum allowed number of items. Ignored if `length` is also given.
        length: Exact required number of items. Conflicts with
            min_length/max_length (raises ParamError — validated by
            HasLength itself).
        unique: If True, every item in the container must be unique (AllUnique).
        has_item: If given, the value must contain this single item (HasItem).
        subset_of: If given, every item in the value must appear in this
            reference collection (IsSubsetOf).
        superset_of: If given, every item in this reference collection
            must appear in the value (IsSupersetOf).
        for_each: If given, every item in the value must satisfy this rule
            or callable (ForEach) — e.g. `container_rule(for_each=is_integer)`.

    Returns:
        A single Rule instance — `is_container` itself if no constraint is
        given, otherwise an AllOf combining the type check with every
        given constraint.
    """
    # 1. Base type check
    parts: list[Rule] = [_is_container]

    # 2. Length — passed through as-is; HasLength validates the
    #    length vs. min_length/max_length conflict itself
    if length is not None or min_length is not None or max_length is not None:
        parts.append(_has_length(length, min_length=min_length, max_length=max_length))

    # 3. Uniqueness
    if unique:
        parts.append(_all_unique)

    # 4. Single-item membership
    if has_item is not None:
        parts.append(_has_item(has_item))

    # 5. Subset
    if subset_of is not None:
        parts.append(_is_subset_of(subset_of))

    # 6. Superset
    if superset_of is not None:
        parts.append(_is_superset_of(superset_of))

    # 7. Per-item rule
    if for_each is not None:
        parts.append(ForEach(for_each))

    # 8. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# container_rule — Composed Container Validation Rule

## Purpose
Layer-3 composition over `IsContainer` (layer 1) / `is_container` (layer 2).
See `string_rule.py`'s design notes for the shared pattern (private
shortcut aliases, `None` as the unconstrained sentinel, the zero-overhead
empty case). This file only documents what is specific to containers.

---

## 1. `for_each` Is a Different Kind of Parameter Than the Rest

Every other parameter here takes a plain value and internally builds one
fixed rule from it. `for_each` takes an entire `Rule` (or callable)
supplied by the caller and wraps it in `ForEach` — validating container
*contents* still requires reaching back into layer 1/2 for the per-item
rule:

    container_rule(min_length=1, for_each=is_integer)
    container_rule(for_each=int_rule(greater_than=0))

This is intentional: enumerating "the most common per-item constraints"
as flattened parameters here would either duplicate every other composed
rule as parameters of this one function, or force picking an arbitrary
subset. Accepting a `Rule` directly keeps this function small while still
composing with anything else in the library.

---

## 2. `has_item` vs. `subset_of`/`superset_of`

`has_item` checks a single item's membership (`HasItem`); `subset_of`/
`superset_of` compare the *whole* container against a reference
collection. `has_item=x` is not a special case expressible more cheaply
via the other two without an awkward one-element collection — it is kept
as its own parameter for the common "does this contain X" case.

---

## 3. `unique` Is a Real Flag, Not a Sentinel

Unlike `has_item`/`subset_of`/`superset_of`/`for_each` (which have no
meaningful "off" value other than not being given), `unique` is a plain
`bool`: `False` is itself a fully meaningful, intentional default ("no
uniqueness constraint"), so there is no ambiguity to guard against with
`None`.

---

## 4. Deliberately Out of Scope

* **Mapping-specific checks** (`has_key`, `has_keys`) — see `mapping_rule.py`,
  which layers on top of `IsInstance(dict)` instead of `IsContainer`.
* **Ordering constraints** (e.g. "must be sorted") — no layer-1 rule for
  this exists yet.
"""