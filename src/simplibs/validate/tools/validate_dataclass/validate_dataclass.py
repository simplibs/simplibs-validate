import dataclasses
import functools
import inspect
from typing import Any, Callable, TypeVar, overload
# Outers
from ...rules.base_class import Rule
from ..validate_call._helpers import compile_parameter_rules
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

    # 3. Compile every field's Rule once, at decoration time — reusing
    #    validate_call's own per-parameter compiler unchanged
    original_init = cls.__init__
    signature = inspect.signature(original_init)
    compiled = compile_parameter_rules(original_init, signature, check=check, overrides=overrides or {})
    context = get_dataclass_context_string(cls)

    # 4. Wrap __init__ — validates raw constructor arguments before any
    #    field is assigned onto self (matters for frozen dataclasses:
    #    nothing is ever set if validation fails)
    @functools.wraps(original_init)
    def wrapper(self: C, *args: Any, **kwargs: Any) -> None:

        # 4.1 Bind call arguments to signature
        bound = signature.bind(self, *args, **kwargs)
        bound.apply_defaults()

        # 4.2 Validate arguments against parameter rules
        for name, value in bound.arguments.items():
            rule = compiled.get(name)
            if rule is not None:
                rule.validate(value, value_name=name, context=context)

        # 4.3 Execute original __init__ constructor
        # noinspection PyArgumentList
        original_init(self, *args, **kwargs)

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
`self` is skipped automatically (no annotation, no override — the same
mechanism validate_call already relies on for its own `self`-less
functions). This is why validate_dataclass has no _helpers/ of its own:
there is no dataclass-specific decision to make that
compile_parameter_rules doesn't already make identically well.

---

## 2. Why This Exists at All, Given `validate_call` Already Works on `__init__`

An ordinary class's hand-written `__init__` can already be decorated
directly with `@validate_call` — no gap exists there.
`@dataclasses.dataclass` is different: it *generates* `__init__` itself,
so there is nothing to decorate at the point the class body is written.
validate_dataclass exists specifically to run *after* that generation —
decorator order (`@validate_dataclass` above `@dataclass`) is what makes
this possible, and is enforced at decoration time via
raise_not_a_dataclass_error rather than failing confusingly deeper inside
compile_parameter_rules if the order is reversed.

---

## 3. Validates Before Assignment, Not After (`__post_init__`)

Wrapping `__init__` itself — rather than adding logic to
`__post_init__` — means every field is checked against raw constructor
arguments before any of them are ever assigned onto `self`. For a frozen
dataclass in particular, this guarantees an invalid instance is never
even partially constructed: validation failure raises before
`original_init` (and therefore any `object.__setattr__` frozen-dataclass
assignment) ever runs. It also avoids any interference with a
user-defined `__post_init__` — dataclasses.dataclass already calls it
from inside the generated `__init__` it creates, so wrapping that
`__init__` wraps the user's own `__post_init__` call transparently,
without needing to detect, chain, or replace it.

---

## 4. No `check_return` Equivalent

A dataclass's `__init__` always returns `None` — there is no return
value analogous to validate_call's `check_return` to offer here. This is
a structural fact about `__init__`, not an omitted feature.

---

## 5. `@overload` Mirrors validate_call's, for a Class Instead of a Function

Same rationale as validate_call's own `@overload` pair (see its design
notes) — `type[C]` in place of `Callable[P, R]`, since this decorator
transforms and returns a class, not a function. No `ParamSpec` is needed
here: unlike validate_call, this decorator doesn't need to preserve a
*call* signature for IDEs — it returns the same class object, whose own
`__init__` signature is untouched by inspection tools even though its
implementation is now wrapped.

---

## 6. Why There Is No Async Branch

Unlike `validate_call` or `log_this`, `validate_dataclass` does not 
provide an `async def` wrapper branch. In Python, class constructors 
(`__init__`) are language-enforced to be purely synchronous — an `__init__` 
method can never be an `async def` coroutine function 
(instantiation syntax `obj = MyClass()` cannot be awaited). 
Since `@dataclasses.dataclass` always generates a synchronous `__init__`, 
`inspect.iscoroutinefunction(original_init)` would evaluate to `False` in 100% of cases. 
The async wrapper pattern is therefore structurally unnecessary here.
"""