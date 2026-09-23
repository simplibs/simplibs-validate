import dataclasses
import functools
import inspect
from typing import Any, Callable, TypeVar, overload
from simplibs.rules import Rule
# Outers
from ..validate_call import compile_parameter_rules
# Inners
from ._helpers import get_dataclass_context_string
from ._validations import raise_not_a_dataclass_error
# Annotations
C = TypeVar("C")


# ============================================================================
# Typing overloads — resolved at type-check time only, never executed.
# See validate_call's own design notes for the general @overload rationale;
# mirrored here for a class decorator instead of a function decorator.
# ============================================================================

@overload
def validate_dataclass(cls: type[C]) -> type[C]: ...


@overload
def validate_dataclass(
    cls: None = None,
    *,
    check: tuple[str, ...] | None = None,
    overrides: dict[str, Rule | Callable[[Any], bool]] | None = None,
) -> Callable[[type[C]], type[C]]: ...


# ============================================================================
# Actual implementation
# ============================================================================

def validate_dataclass(
    cls: type[C] | None = None,
    *,
    check: tuple[str, ...] | None = None,
    overrides: dict[str, Rule | Callable[[Any], bool]] | None = None,
) -> type[C] | Callable[[type[C]], type[C]]:
    """Validate every field of a dataclass against its own annotations,
    on every instance construction.

    Must be applied *above* @dataclasses.dataclass (decorators apply
    bottom-up, so @dataclass needs to have already generated __init__ by
    the time this decorator runs):

        @validate_dataclass
        @dataclass
        class User:
            name: str
            age: Annotated[int, greater_than(0)]

    Internally, this wraps the dataclass-generated __init__ using the
    exact same compile_parameter_rules machinery validate_call uses for
    ordinary functions — a dataclass's __init__ signature (one parameter
    per field, carrying that field's own annotation) is structurally
    identical to any other function's signature from that helper's point
    of view, so no separate rule-building logic exists here.

    Applying this decorator twice to the same class (directly, or
    indirectly via re-decoration in generated/derived code) is detected
    and short-circuited — see the design notes below.

    Args:
        cls: The dataclass to wrap. Omit when using
            `@validate_dataclass(...)` with keyword arguments; present
            when used as bare `@validate_dataclass`.
        check: If given, only these field names are validated — every
            other annotated field is left unchecked. Every name listed
            here must have either an annotation or an entry in
            `overrides` (checked at decoration time — see ParamError below).
        overrides: Extra Rule/callable predicates per field name,
            combined via AllOf with whatever the field's own annotation
            already produces.

    Returns:
        The same class, with __init__ replaced by a validating wrapper.

    Raises:
        ParamError: If `cls` is not a dataclass, or if `check` names a
            field that has neither an annotation nor an `overrides` entry.
    """
    # 1. Support both @validate_dataclass and @validate_dataclass(...)
    if cls is None:
        return lambda c: validate_dataclass(c, check=check, overrides=overrides)

    # 2. Must already be a dataclass — see raise_not_a_dataclass_error
    if not dataclasses.is_dataclass(cls):
        raise_not_a_dataclass_error(cls)

    # 3. Guard against double-wrapping: if this class's __init__ was
    #    already wrapped by a previous @validate_dataclass application,
    #    peel that wrapper off before compiling new rules, so re-applying
    #    this decorator never stacks two independent validating layers.
    original_init = cls.__init__
    while getattr(original_init, "_is_validate_dataclass_wrapper", False):
        next_layer = getattr(original_init, "__wrapped__", None)
        if next_layer is None:
            break
        original_init = next_layer

    # 4. Compile every field's Rule once, at decoration time — reusing
    #    validate_call's own per-parameter compiler unchanged
    signature = inspect.signature(original_init)
    compiled = compile_parameter_rules(original_init, signature, check=check, overrides=overrides or {})
    context = get_dataclass_context_string(cls)

    # 5. Wrap __init__ — validates raw constructor arguments before any
    #    field is assigned onto self (matters for frozen dataclasses:
    #    nothing is ever set if validation fails)
    @functools.wraps(original_init)
    def wrapper(self: C, *args: Any, **kwargs: Any) -> None:

        # 5.1 Bind call arguments to signature
        bound = signature.bind(self, *args, **kwargs)
        bound.apply_defaults()

        # 5.2 Validate arguments against parameter rules
        for name, value in bound.arguments.items():
            rule = compiled.get(name)
            if rule is not None:
                rule.validate(value, value_name=name, context=context)

        # 5.3 Execute original __init__ constructor
        # noinspection PyArgumentList
        original_init(self, *args, **kwargs)

    # 6. Mark wrapper for future unwrap/double-decoration inspection
    wrapper._is_validate_dataclass_wrapper = True  # type: ignore[attr-defined]

    cls.__init__ = wrapper
    return cls


_DESIGN_NOTES = """
# validate_dataclass — Annotation-Driven Dataclass Field Validation

## Purpose
The dataclass counterpart to validate_call: every field is validated
against the Rule build_typing_rule builds from its annotation, on every
instance construction — reusing validate_call's own per-parameter
compiler rather than duplicating it.

---

## 1. Why This Needs No New Rule-Building Logic

A dataclass-generated __init__ has exactly one parameter per field, each
carrying that field's own type annotation — structurally the same shape
compile_parameter_rules already processes for any ordinary function.
`self` is skipped automatically, the same mechanism validate_call already
relies on for its own `self`-less functions.

---

## 2. Why This Exists at All, Given `validate_call` Already Works on `__init__`

An ordinary class's hand-written `__init__` can already be decorated
directly with `@validate_call`. `@dataclasses.dataclass` is different: it
*generates* `__init__` itself, so there is nothing to decorate at the
point the class body is written. validate_dataclass exists specifically
to run *after* that generation — decorator order (`@validate_dataclass`
above `@dataclass`) is enforced at decoration time via
`raise_not_a_dataclass_error`.

---

## 3. Validates Before Assignment, Not After (`__post_init__`)

Wrapping `__init__` itself means every field is checked against raw
constructor arguments before any of them are ever assigned onto `self`.
For a frozen dataclass, this guarantees an invalid instance is never
even partially constructed. It also transparently wraps any
user-defined `__post_init__`, since `dataclasses.dataclass` already
calls it from inside the generated `__init__` this decorator wraps.

---

## 4. No `check_return` Equivalent

A dataclass's `__init__` always returns `None` — a structural fact, not
an omitted feature.

---

## 5. `@overload` Mirrors validate_call's, for a Class Instead of a Function

`type[C]` in place of `Callable[P, R]`. No `ParamSpec` is needed here —
this decorator returns the same class object, whose own `__init__`
signature is untouched by inspection tools even though its
implementation is now wrapped.

---

## 6. Why There Is No Async Branch

Class constructors (`__init__`) are language-enforced to be purely
synchronous — instantiation syntax `obj = MyClass()` cannot be awaited.
`inspect.iscoroutinefunction(original_init)` would evaluate to `False` in
100% of cases for a dataclass-generated `__init__`, so an async wrapper
branch would be structurally unreachable dead code.

---

## 7. Double-Wrapping Guard (`_is_validate_dataclass_wrapper`) — Added for
Consistency With `validate_call`/`log_this`

This gap did not exist in an earlier revision of this file: applying
`@validate_dataclass` twice to the same class — directly, or by
re-running a decoration step against an already-decorated class in some
generated/derived code path — stacked two independent wrapper layers
around `__init__` with no detection at all, silently validating every
field twice per construction. `validate_call` and `log_this` both
already guard against this for functions via their own
`unwrap_validate_call`/`unwrap_log_this` helpers and
`_is_*_wrapper` markers; this decorator now follows the identical
pattern for classes: `wrapper` is marked with
`_is_validate_dataclass_wrapper = True`, and before compiling new rules,
any existing wrapper layer already carrying that marker is peeled off
via its `__wrapped__` chain (the same safe, `break`-terminated pattern
used by `unwrap_validate_call`/`unwrap_log_this` — see their own design
notes for why the non-terminating nested-`getattr` version was
incorrect).

Kept inline here rather than factored into a standalone
`unwrap_validate_dataclass` helper file, since this decorator's
`_helpers/` package does not otherwise exist yet and a four-line loop
does not yet justify introducing one — revisit if a second caller ever
needs the same unwrap logic independently of this decorator.

No bypass-parameter mechanism (`_validate_call`-equivalent) has been
added alongside this guard — dataclass construction has no established
per-call reason to skip validation the way a repeatedly-invoked function
does (see `create_act.py`'s own design notes for why that mechanism
exists where it does). Add one later if a concrete need appears; nothing
here forecloses it.
"""
