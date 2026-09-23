# >>> src/simplibs/validate/rules/typing/validated_type.py
from typing import Annotated, Any, Callable
# Outers
from ...rules.base_class import Rule
# Inners
from ._validations import (
    raise_validated_type_missing_rule_error,
    raise_validated_type_rule_invalid_error,
)


def validated_type(
    type_: Any,
    *rules: Rule | Callable[[Any], bool]
) -> Any:
    """Build Annotated[type_, *rules] for use directly as a parameter, field,
    or variable annotation.

    Multiple rules may be given either as separate positional arguments,
    or pre-composed via |/&/~ — both produce the same final Rule once
    decomposed:

        PositiveInt = validated_type(int, greater_than(0))
        PositiveInt = validated_type(int, is_integer, greater_than(0))
        PositiveInt = validated_type(int, is_integer & greater_than(0))

    Example:
        my_int = validated_type(int, greater_than(0))

        @validate_call
        def register(age: my_int): ...

    Args:
        type_: The underlying type or typing construct (int, list[int],
            int | None, ...) — anything build_typing_rule already accepts.
        *rules: One or more Rule instances or plain callable predicates.
            At least one is required. When more than one is given, they
            are attached to type_ as separate Annotated metadata items —
            annotated_builder combines every recognized Rule/callable
            metadata item via AllOf when the resulting annotation is
            later decomposed (via build_typing_rule/IsTyping), exactly as
            if each had been listed by hand in `Annotated[type_, rule1,
            rule2, ...]`.

    Returns:
        Annotated[type_, *rules] — an ordinary typing construct. This
        function performs no decomposition itself; that happens later,
        whenever build_typing_rule processes the resulting annotation.

    Raises:
        ParamError: If no rules are given, or if any rule is neither a
            Rule instance nor callable.
    """
    # 1. At least one rule is required — see design notes, section 2
    if not rules:
        raise_validated_type_missing_rule_error(type_)

    # 2. Fail fast on any unusable rule, naming its exact position
    for index, rule in enumerate(rules):
        if not (isinstance(rule, Rule) or callable(rule)):
            raise_validated_type_rule_invalid_error(rule, index)

    # 3. Nothing more to do — this is a thin, honest wrapper
    return Annotated[type_, *rules]


_DESIGN_NOTES = """
# validated_type — Named-Type Construction Helper

## Purpose
A thin, named wrapper around `Annotated[type_, *rules]` — lets a caller
define a reusable "type + validation rule(s)" once and reference it by
name, instead of repeating `Annotated[int, greater_than(0)]` inline at
every usage site:

    PositiveInt = validated_type(int, greater_than(0))

    def f(x: PositiveInt): ...
    def g(y: PositiveInt): ...

---

## 1. Zero Deferral — This Is Not Lazy

`validated_type()` builds and returns the Annotated construct
immediately; nothing about the rules is inspected against a value or
decomposed here. Actual decomposition happens later, whenever
build_typing_rule (via IsTyping, validate_call, or validate_dataclass)
processes the resulting annotation — annotated_builder already knows how
to unpack Rule/callable metadata from any Annotated construct, whether
built by hand or through this helper. This function exists purely for
naming convenience and input validation, not as a new mechanism.

Written as `Annotated[type_, *rules]` (star-unpacked directly in the
subscript), not `Annotated[(type_, *rules)]` — both are runtime-identical
(a comma-separated subscript always builds a tuple either way), but the
un-parenthesized form is what static type checkers (PyCharm, mypy)
recognize correctly; the parenthesized tuple form triggers a false
"Annotated must be called with at least two arguments" warning in
PyCharm, since its checker does not special-case unpacking inside an
inner tuple literal.

---

## 2. `*rules` — Two Equivalent Ways to Combine Multiple Constraints

`validated_type(int, is_integer, greater_than(0))` and
`validated_type(int, is_integer & greater_than(0))` produce behaviorally
identical results once decomposed — annotated_builder combines every
Rule/callable metadata item it finds via AllOf regardless of whether
that item is itself already a composed Rule (from `&`) or one of several
separate items in the tuple. This is a deliberate accommodation of two
different authoring preferences rather than two different mechanisms:

* Explicit `&` composition keeps a strong visual boundary between "this
  first argument is the type" and "this is the (possibly compound) rule"
  — every rule is one, clearly-delimited expression.
* A flat comma-separated list reads naturally as "the type, followed by
  a list of conditions", and is easier to build programmatically (e.g.
  appending conditions to a list and unpacking it with `*`) than folding
  a growing chain of `&`-joined rules at runtime.

Both styles can also be freely mixed in one call
(`validated_type(int, is_integer & greater_than(0), less_than(100))`) —
AllOf's own constructor already flattens nested AllOf instances (see its
design notes), so no special handling is needed here for that case.

---

## 3. At Least One Rule Is Required

`validated_type(int)` with zero rules is never a meaningful call — the
caller should write `int` directly as the annotation in that case, not
reach for validated_type at all. Enforced immediately via
raise_validated_type_missing_rule_error rather than silently producing a
technically-valid but pointless `Annotated[int]`.

---

## 4. Every Rule Is Validated, Not Just the First

Each of `*rules` is checked individually (Rule instance or callable),
with its position reported on failure — a multi-rule call
(`validated_type(int, is_integer, some_typo)`) points precisely at which
argument is wrong, rather than a generic "one of your rules is invalid"
that would leave the caller to check every one by hand.
"""