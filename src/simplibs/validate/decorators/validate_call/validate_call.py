import functools
import inspect
from typing import Any, Callable, ParamSpec, TypeVar, overload
from simplibs.rules import Rule
# Inners
from ._validations import raise_no_iterable_parameter
from ._helpers import (
    compile_parameter_rules,
    compile_return_rule,
    find_iterable_parameters,
    get_context_string,
    is_bypass_parameter,
    lazy_signature_state,
    materialize_iterator_arguments,
    should_validate,
    unwrap_validate_call,
)
# Annotations
P = ParamSpec("P")
R = TypeVar("R")


# ============================================================================
# Typing overloads — resolved at type-check time only, never executed.
# See validate_call's own design notes, section 6, for why these exist.
# ============================================================================

@overload
def validate_call(func: Callable[P, R]) -> Callable[P, R]: ...


@overload
def validate_call(
    func: None = None,
    *,
    check: tuple[str, ...] | None = None,
    overrides: dict[str, Rule | Callable[[Any], bool]] | None = None,
    check_return: bool = False,
    materialize_iterators: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


# ============================================================================
# Actual implementation
# ============================================================================

def validate_call(
    func: Callable[P, R] | None = None,
    *,
    check: tuple[str, ...] | None = None,
    overrides: dict[str, Rule | Callable[[Any], bool]] | None = None,
    check_return: bool = False,
    materialize_iterators: bool = False,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Validate a function's arguments (and optionally its return value)
    against its own annotations at call time.

    Every annotated parameter is validated against the Rule that
    IsTyping/build_typing_rule would build for it — a plain type, a
    typing generic (list[int], int | None, ...), an Annotated[...]
    wrapping Rule metadata, or a Rule instance used directly as the
    annotation. Unannotated parameters are skipped unless named in
    `overrides`.

    If the function declares a reserved "_validate_call" parameter (bool or
    unannotated — see is_bypass_parameter), its value at call time
    controls whether validation runs at all for that call: True (or the
    parameter's default) validates normally, False skips every check for
    both parameters and the return value. Functions without such a
    parameter always validate — this is purely opt-in per function.

    Works identically on `async def` functions: parameters are validated
    synchronously before the call, exactly as for a sync function, and
    the return value is validated only after being awaited — never a
    bare, unresolved coroutine object.

    Args:
        func: The function to wrap. Omit when using `@validate_call(...)`
            with keyword arguments; present when used as bare `@validate_call`.
        check: If given, only these parameter names are validated —
            every other annotated parameter is left unchecked. Every name
            listed here must have either an annotation or an entry in
            `overrides` (checked at decoration time — see ParamError below).
        overrides: Extra Rule/callable predicates per parameter name,
            combined via AllOf with whatever the parameter's own
            annotation already produces (or used alone, if the parameter
            has no annotation at all).
        check_return: If True, the return value is also validated against
            the function's `-> ...` annotation. Raises at decoration time
            if True but no return annotation exists.
        materialize_iterators: If True, a one-shot iterator (generator,
            map, file, ...) passed to a parameter annotated as `Iterable[T]`
            is consumed once and replaced by a tuple, instead of being
            rejected — the function receives that tuple. Off by default, so
            iterators stay rejected unless this is chosen consciously.
            Parameters annotated as bare `Iterable`, and nested ones such
            as `list[Iterable[int]]`, are not affected.

    Returns:
        The wrapped function, validating on every call.

    Raises:
        ParamError: At decoration time, if `check` names a parameter that
            has neither an annotation nor an `overrides` entry, or if
            `check_return=True` is given but the function has no return
            annotation, or if `materialize_iterators=True` is given but no
            validated parameter is annotated as `Iterable[T]`, or if an
            annotation cannot be resolved. When an annotation refers to a name
            that does not exist yet at decoration time (a class defined further
            down the module, a method annotated with its own class), these
            checks happen on the first call instead.
    """

    # 1. Support both @validate_call and @validate_call(...) syntax forms
    if func is None:
        return lambda f: validate_call(
            f,
            check=check,
            overrides=overrides,
            check_return=check_return,
            materialize_iterators=materialize_iterators,
        )

    # 2. Peel off existing @validate_call wrappers to prevent double validation
    raw_func = unwrap_validate_call(func)

    # 3. Binding needs only parameter names, which are always available
    signature = inspect.signature(raw_func)
    context = get_context_string(raw_func)
    has_bypass = any(is_bypass_parameter(p) for p in signature.parameters.values())

    # 4. Rules need real annotation objects. They are built once — at decoration
    #    time when every annotation can be resolved, otherwise on the first call
    #    (a name used in an annotation may not exist yet while the module loads)
    def build_state(resolved: inspect.Signature) -> tuple[dict[str, Rule], Rule | None, tuple[str, ...]]:
        compiled = compile_parameter_rules(raw_func, resolved, check=check, overrides=overrides or {})
        return_rule = compile_return_rule(raw_func, resolved, check_return=check_return)
        iterable_names = (
            find_iterable_parameters(resolved, frozenset(compiled)) if materialize_iterators else ()
        )
        if materialize_iterators and not iterable_names:
            raise_no_iterable_parameter(raw_func)
        return compiled, return_rule, iterable_names

    get_state = lazy_signature_state(raw_func, build_state)

    # 5. Async functions need an async wrapper so the return-value rule
    #    validates the awaited result, not a bare coroutine object
    if inspect.iscoroutinefunction(raw_func):

        @functools.wraps(raw_func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            # 5.1 Rules (cached after the first call)
            compiled, return_rule, iterable_names = get_state()

            # 5.2 Bind call arguments to signature
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            validate = should_validate(bound, has_bypass=has_bypass)

            # 5.3 Replace one-shot iterators (opt-in) before they are validated
            if validate and materialize_iterator_arguments(bound, iterable_names):
                args, kwargs = bound.args, bound.kwargs

            # 5.3.1 Validate arguments against parameter rules
            if validate:
                for name, value in bound.arguments.items():
                    rule = compiled.get(name)
                    if rule is not None:
                        rule.validate(value, value_name=name, context=context)

            # 5.4 Execute target async function
            result = await raw_func(*args, **kwargs)

            # 5.5 Validate return value if requested
            if validate and return_rule is not None:
                return_rule.validate(result, value_name="return value", context=context)

            # 5.6 Return validated result
            return result

        # 5.7 Mark wrapper for future unwrap inspection
        async_wrapper._is_validate_call_wrapper = True  # type: ignore[attr-defined]
        return async_wrapper

    # 6. Plain synchronous wrapper
    @functools.wraps(raw_func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

        # 6.1 Rules (cached after the first call)
        compiled, return_rule, iterable_names = get_state()

        # 6.2 Bind call arguments to signature
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        validate = should_validate(bound, has_bypass=has_bypass)

        # 6.3 Replace one-shot iterators (opt-in) before they are validated
        if validate and materialize_iterator_arguments(bound, iterable_names):
            args, kwargs = bound.args, bound.kwargs

        # 6.3.1 Validate arguments against parameter rules
        if validate:
            for name, value in bound.arguments.items():
                rule = compiled.get(name)
                if rule is not None:
                    rule.validate(value, value_name=name, context=context)

        # 6.4 Execute target function
        result = raw_func(*args, **kwargs)

        # 6.5 Validate return value if requested
        if validate and return_rule is not None:
            return_rule.validate(result, value_name="return value", context=context)

        # 6.6 Return validated result
        return result

    # 6.7 Mark wrapper for future unwrap inspection
    sync_wrapper._is_validate_call_wrapper = True  # type: ignore[attr-defined]
    return sync_wrapper


_DESIGN_NOTES = """
# validate_call — Annotation-Driven Argument Validation Decorator

## Purpose
Applies IsTyping's decomposition to an entire function signature at once:
every annotated parameter (and optionally the return value) is validated
on every call, using exactly the same Rule-building machinery IsTyping
already provides — no parallel logic for interpreting annotations exists
here.

---

## 1. Why This Needs No Case-1/2/3 Branching of Its Own

A parameter's annotation can be a bare Rule instance, an Annotated[...]
wrapping Rule metadata, or an ordinary typing construct — all three are
handled identically by build_typing_rule itself. This decorator never
needs to ask "what kind of annotation is this" — that question belongs
entirely to IsTyping's decomposition layer, not to this one.

---

## 2. All Compilation Logic Lives in Dedicated Helpers

`compile_parameter_rules` (per-parameter: annotation + override + `check`
filtering) and `compile_return_rule` (the single return-value rule +
`check_return` guard) hold every real decision this decorator makes about
*what* to validate. This file itself contains none of that logic — only
the `@validate_call`/`@validate_call(...)` dispatch and the wrapper
closure that calls into both.

---

## 3. Unwrapping and Compilation Happen Once, at Decoration Time

`validate_call` invokes `unwrap_validate_call` prior to inspection to ensure
no redundant `@validate_call` layers are stacked. Every helper
(`compile_parameter_rules`, `compile_return_rule`, and the `has_bypass` check)
runs exactly once, when `@validate_call` is applied to a function — never per
call.

---

## 4. `bound.apply_defaults()` — Defaults Are Validated Too

Without this, a parameter left at its default value would never appear
in `bound.arguments` and would silently skip validation — including
cases where the default itself violates the parameter's own annotation.

---

## 5. Return-Value Validation Is Opt-In, and Symmetric With `check`'s Guard

`check_return` defaults to False. When explicitly requested but no return
annotation exists, `compile_return_rule` raises at decoration time.

---

## 6. `@overload` for Full Signature-Preserving Type Hints

Two `@overload` signatures precede the real implementation — see
`is_bypass_parameter`/`should_validate`'s own docs for the bypass
mechanism and `create_action`'s own design notes for how it composes
with dynamically-generated functions.

---

## 7. Async Functions Get Their Own Wrapper Branch

Parameter validation itself never needs to be async — every argument is
known before the call starts. What differs for a coroutine function is
only how its **result** is obtained (must be awaited before the return
rule can validate it, not a bare coroutine object).

---

## 8. The Reserved Bypass Switch (`_validate_call`) — No Kwargs Stripping Needed

`is_bypass_parameter` only ever reports `has_bypass=True` for a function
that *itself declares* a parameter literally named `_validate_call` in
its own signature — that is exactly how `has_bypass` is computed
(`any(is_bypass_parameter(p) for p in signature.parameters.values())`).
This means whenever `_validate_call` is a valid keyword for a given call,
it is *already* one of `raw_func`'s own real parameters — `raw_func(*args,
**kwargs)` calling with it present is correct, expected behavior, not
something that needs to be filtered out first.

An earlier revision of this wrapper contained a `clean_kwargs` block that
attempted to strip `_validate_call` from `kwargs` before calling
`raw_func` whenever `_validate_call not in signature.parameters` — but
that condition can never be true when `has_bypass` is also true, since
`has_bypass` itself is only ever set by finding `_validate_call` inside
`signature.parameters` in the first place. The block was unreachable
dead code and has been removed. (It was also unreachable for the
opposite reason on functions with `has_bypass=False`: `signature.bind()`
two lines above it already raises `TypeError` for an unexpected
`_validate_call` keyword before that code could ever run.)

Per this decorator's own documented contract, `_validate_call` — when a
function declares it — is "passed through to the function body unchanged,
so the function can inspect or forward it if it wants to." A function
that wants to silently swallow the flag rather than act on it (as
`create_action`'s generated `act` does, deliberately never forwarding it
into the wrapped business function — see `create_act.py`'s own design
notes) is responsible for doing that itself, inside its own body. That
decision belongs to the function being decorated, not to this decorator.

---

## 9. Selective Wrapper Marker (`_is_validate_call_wrapper`)

Both returned wrappers attach `_is_validate_call_wrapper = True`.
This explicit marker enables `unwrap_validate_call` to surgically identify and
peel away prior `@validate_call` layers without stripping away arbitrary user
decorators (such as `@cache` or `@retry`).

---

## 10. `materialize_iterators` — Opt-In Conversion Instead of Rejection

`Iterable[T]` rejects one-shot iterators (IsReiterable), because validating
one would silently exhaust it before the function ever runs. Rejection stays
the default. `materialize_iterators=True` lets the caller of the decorator
choose, consciously, to consume the iterator once and hand the function a
tuple instead — so nothing is changed silently.

* **Scope:** only validated parameters annotated `Iterable[T]` (also inside
  a union or `Annotated`). Bare `Iterable` is never rejected and so is never
  converted — a function that wants the lazy iterator keeps it. Detected once
  at decoration time (find_iterable_parameters).
* **Call time:** materialize_iterator_arguments replaces Iterator arguments
  in `bound.arguments`. Only when something was converted does the wrapper
  call the function with `bound.args` / `bound.kwargs`; otherwise the original
  `args` / `kwargs` are used unchanged.
* **Bypass:** with `_validate_call=False` nothing is converted — a bypassed
  call is passed through exactly as given.
* **Decoration-time guard:** the flag with no eligible parameter raises
  ParamError (raise_no_iterable_parameter) rather than silently doing nothing.
* **Caveat:** infinite or huge iterators are the user's responsibility once
  the flag is on.

---

## 11. String Annotations and Forward References

Annotations written as strings — by hand, or all of them at once by
`from __future__ import annotations` — are turned into real objects before any
rule is built (resolve_signature), so build_typing_rule, the `Iterable[T]`
detection and the return-value rule always see actual types. Annotations that
are already objects are never touched, so existing code behaves as before.

* **Binding is separate from resolving.** `signature.bind(...)` needs only
  parameter names, so the wrapper binds with the plain signature and never
  depends on resolution.
* **Early when possible, late when needed.** If every name exists while the
  decorator runs, the rules are built immediately and configuration errors are
  raised at decoration time as always. If a name does not exist yet — a method
  annotated with its own class, a class defined further down the module — the
  rules are built on the first call and cached (lazy_signature_state); the
  configuration errors of that one function are then raised on that first call.
* **Still missing at the first call** is reported by
  raise_unresolvable_annotation (a class defined inside another function, a name
  imported only under TYPE_CHECKING, a typo).
"""
