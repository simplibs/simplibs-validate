from typing import Any, Container
from simplibs.rules import (
    Rule,
    AllOf,
    is_string as _is_string,
    has_length as _has_length,
    starts_with as _starts_with,
    ends_with as _ends_with,
    contains as _contains,
    is_substring_of as _is_substring_of,
    regex as _regex,
    is_blank as _is_blank,
    not_blank as _not_blank,
    equals as _equals,
    not_equals as _not_equals,
    is_in as _is_in,
    not_in as _not_in,
)


def string_rule(
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    length: int | None = None,
    starts_with: str | None = None,
    ends_with: str | None = None,
    contains: str | None = None,
    is_substring_of: str | None = None,
    regex_search: str | None = None,
    is_blank: bool | None = None,
    equals: str | None = None,
    not_equals: str | None = None,
    is_in: Container[Any] | None = None,
    not_in: Container[Any] | None = None,
) -> Rule:
    """Compose a Rule validating a string against the given optional constraints.

    Args:
        min_length: Minimum allowed length. Ignored if `length` is also given.
        max_length: Maximum allowed length. Ignored if `length` is also given.
        length: Exact required length. Conflicts with min_length/max_length
            (raises ParamError — validated by HasLength itself).
        starts_with: Required prefix.
        ends_with: Required suffix.
        contains: Required substring.
        is_substring_of: Target string in which the evaluated string must be contained.
        regex_search: Required regular expression pattern, matched anywhere
            in the string via `re.search` (not an anchored full match).
        is_blank: If None (default), blankness is unconstrained. If True, the
            string must be blank (empty or whitespace-only). If False, the
            string must NOT be blank.
        equals: The value must equal this exact string.
        not_equals: The value must NOT equal this exact string.
        is_in: The value must be one of the given options.
        not_in: The value must NOT be one of the given options.

    Returns:
        A single Rule instance — `is_string` itself if no constraint is
        given, otherwise an AllOf combining the type check with every
        given constraint.
    """
    # 1. Base type check
    parts = [_is_string]

    # 2. Length — passed through as-is; HasLength validates the
    #    length vs. min_length/max_length conflict itself
    if length is not None or min_length is not None or max_length is not None:
        parts.append(_has_length(length, min_length=min_length, max_length=max_length))

    # 3. Prefix
    if starts_with is not None:
        parts.append(_starts_with(starts_with))

    # 4. Suffix
    if ends_with is not None:
        parts.append(_ends_with(ends_with))

    # 5. Substring
    if contains is not None:
        parts.append(_contains(contains))

    # 6. Inverse substring
    if is_substring_of is not None:
        parts.append(_is_substring_of(is_substring_of))

    # 7. Regex search
    if regex_search is not None:
        parts.append(_regex(regex_search))

    # 8. Blankness — tri-state (unconstrained / must be blank / must not be blank)
    if is_blank is not None:
        parts.append(_is_blank if is_blank else _not_blank)

    # 9. Exact equality
    if equals is not None:
        parts.append(_equals(equals))

    # 10. Exact inequality
    if not_equals is not None:
        parts.append(_not_equals(not_equals))

    # 11. Membership
    if is_in is not None:
        parts.append(_is_in(is_in))

    # 12. Non-membership
    if not_in is not None:
        parts.append(_not_in(not_in))

    # 13. Collapse to a single Rule
    return (
        AllOf(*parts)
        if len(parts) > 1
        else parts[0]
    )


_DESIGN_NOTES = """
# string_rule — Composed String Validation Rule

## Purpose
Layer-3 composition over the individual string/comparison predicates
(layer 1 classes, layer 2 snake_case shortcuts), covering the common
string constraints as a single Rule built from at most one AllOf.

---

## 1. Private Shortcut Imports

Every composed shortcut used to build `parts` is imported under a
leading-underscore alias (`is_string as _is_string`, ...). This is a
deliberate naming reservation, not an obfuscation: it frees the public
parameter names (`starts_with`, `contains`, `is_substring_of`, `equals`, ...)
from needing a trailing underscore to avoid shadowing the imported shortcut
of the same name within this function's scope.

---

## 2. `None` as the Universal "Unconstrained" Sentinel

Every parameter here defaults to `None`, not `UNSET`. This is safe
specifically because none of these parameters has a domain in which
`None` is itself a meaningful value to validate against — a string can
never legitimately equal `None`, contain `None`, or have `None` as a
length. `UNSET` earns its keep only where `None` could be ambiguous
between "no constraint" and "the value None itself" (see e.g. a mapping
rule's `has_key_`, where a dict may legitimately have `None` as a key).

---

## 3. `length` — Passed Through, Not Pre-Validated

`length`, `min_length`, and `max_length` are forwarded to `HasLength`
exactly as received, without re-checking the exact-vs-range conflict
here. `HasLength.__init__` already owns that validation (via
`raise_has_length_param_conflict_error`); re-checking it at this layer
would just be the same guard run twice for no benefit.

---

## 4. `is_blank` — Tri-State, Not a Plain Bool

`is_blank` defaults to `None` (no constraint on blankness at all), and only
becomes a constraint when explicitly given: `True` requires the string to
be blank (`IsBlank`), `False` requires it not to be (`NotBlank`).

---

## 5. Zero-Overhead Empty Case

When no constraint is given, `parts` holds only `_is_string`, and step 13
returns it directly rather than wrapping a single rule in `AllOf(...)`.

---

## 6. `regex_search`, Not `pattern`

Named for what it actually does — `Regex` matches via `re.search`
(anywhere in the string), not an anchored full match — so the parameter
name carries that behavior instead of leaving it to be discovered in the
type hint or docstring.

---

## 7. What This Does NOT Cover

Case-insensitive comparison, trimming, or Unicode normalization are
transformations, not predicates, and belong with `Compose` (e.g.
`Compose(str.strip, has_length(min_length=1))`) rather than as parameters
bolted onto this function.
"""