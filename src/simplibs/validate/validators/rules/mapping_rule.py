from typing import Any
from simplibs.sentinels import UNSET, UnsetType
# Outers
from ...rules.base_class import Rule
from ...rules import (
    AllOf,
    is_instance as _is_instance,
    has_length as _has_length,
    has_key as _has_key,
    has_keys as _has_keys,
)


def mapping_rule(
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    has_key: Any | UnsetType = UNSET,
    has_keys: tuple[Any, ...] | None = None,
) -> Rule:
    """Compose a Rule validating a dict against the given optional constraints.

    Args:
        min_length: Minimum allowed number of entries. Ignored if `length` is also given.
        max_length: Maximum allowed number of entries. Ignored if `length` is also given.
        length: Exact required number of entries. Conflicts with
            min_length/max_length (raises ParamError).
        has_key: If given, the value must contain this single key (HasKey).
            Uses the UNSET sentinel rather than None, since None is itself
            a valid dict key and must remain distinguishable from "no
            constraint given".
        has_keys: If given, the value must contain all of these keys
            (HasKeys). Given as a tuple even for a single key, e.g.
            `has_keys=("id",)`.

    Returns:
        A single Rule instance — `IsInstance(dict)` itself if no
        constraint is given, otherwise an AllOf combining the type check
        with every given constraint.
    """
    # 1. Base type check
    parts: list[Rule] = [_is_instance(dict)]

    # 2. Length — passed through as-is; HasLength validates the
    #    length vs. min_length/max_length conflict itself
    if length is not None or min_length is not None or max_length is not None:
        parts.append(_has_length(length, min_length=min_length, max_length=max_length))

    # 3. Single-key membership
    if has_key is not UNSET:
        parts.append(_has_key(has_key))

    # 4. Multi-key membership
    if has_keys is not None:
        parts.append(_has_keys(*has_keys))

    # 5. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# mapping_rule — Composed Dict Validation Rule

## Purpose
Layer-3 composition specifically for `dict` values — the key-membership
counterpart to `container_rule.py`, which intentionally leaves
`has_key`/`has_keys` out (see its design notes, section 3). See
`string_rule.py`'s design notes for the shared pattern this module
follows.

---

## 1. Base Check Is `IsInstance(dict)`, Not `IsContainer`

`IsContainer` accepts any non-string collection. That is too broad a base
for a rule whose purpose is key-membership checks, which only make sense
for mapping types. `is_instance(dict)` narrows the base check to exactly
what this module's constraints assume, at the cost of not covering other
mapping-like types (`OrderedDict`, custom `Mapping` implementations) that
are not literal `dict` subclasses. If broader `Mapping`-protocol support
is needed later, swap the base check for an `IsInstance` against
`collections.abc.Mapping` — no other change here would be required.

---

## 2. `has_key` Is the One Parameter That Still Needs `UNSET`

Every other parameter across the composed-rule modules defaults safely to
`None`, because `None` can never be a legitimate value for what they
constrain (a length, a prefix, a numeric threshold, ...). `has_key` is
the exception in this whole batch: a dict may legitimately use `None`
itself as a key, so `mapping_rule(has_key=None)` — "the value must
contain the key `None`" — has to remain distinguishable from "no key
constraint given at all". Hence `UNSET`/`UnsetType`, imported alongside
`None`-based parameters in the same function without contradiction — each
sentinel is used exactly where it is the only safe choice.

`has_keys` does not need this: the *tuple itself* is never a meaningful
key, even though individual keys inside it may be `None`.

---

## 3. `has_key` and `has_keys` Can Both Be Given

There is no meaningful conflict between requiring one specific key and
requiring a full set of keys — `mapping_rule(has_key="id",
has_keys=("name", "email"))` composes to three independent checks. No
guard was added for this.

---

## 4. Value-Level / Per-Key Validation Is Out of Scope

Validating the *type or shape of individual values* inside the dict
(e.g. "key `'age'` must map to a positive integer") requires composing
`HasKey`/`HasKeys` with `Compose` and a per-key rule — left for direct
manual composition rather than added as a parameter here.
"""