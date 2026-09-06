import functools
import inspect
from typing import Any, Callable, ParamSpec, TypeVar, overload
# Outers
from ...rules.base_class import Rule
# Inners
from ._helpers import (
    compile_parameter_rules,
    compile_return_rule,
    get_context_string,
    is_bypass_parameter,
    should_validate
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
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Validate a function's arguments (and optionally its return value)
    against its own annotations at call time.

    Every annotated parameter is validated against the Rule that
    IsTyping/build_typing_rule would build for it — a plain type, a
    typing generic (list[int], int | None, ...), an Annotated[...]
    wrapping Rule metadata, or a Rule instance used directly as the
    annotation. Unannotated parameters are skipped unless named in
    `overrides`.

    If the function declares a reserved "validate" parameter (bool or
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

    Returns:
        The wrapped function, validating on every call.

    Raises:
        ParamError: At decoration time, if `check` names a parameter that
            has neither an annotation nor an `overrides` entry, or if
            `check_return=True` is given but the function has no return
            annotation.
    """

    # 1. Support both @validate_call and @validate_call(...)
    if func is None:
        return lambda f: validate_call(
            f,
            check=check,
            overrides=overrides,
            check_return=check_return,
        )

    # 2. Compile every rule once, at decoration time
    signature = inspect.signature(func)
    compiled = compile_parameter_rules(func, signature, check=check, overrides=overrides or {})
    return_rule = compile_return_rule(func, signature, check_return=check_return)
    context = get_context_string(func)
    has_bypass = any(is_bypass_parameter(p) for p in signature.parameters.values())

    # 3. Async functions need an async wrapper so the return-value rule
    #    validates the awaited result, not a bare coroutine object — see
    #    this module's design notes, section 7.
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            # 3.1 Bind call arguments to signature
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            validate = should_validate(bound, has_bypass=has_bypass)

            # 3.2 Validate arguments against parameter rules
            if validate:
                for name, value in bound.arguments.items():
                    rule = compiled.get(name)
                    if rule is not None:
                        rule.validate(value, value_name=name, context=context)

            # 3.3 Execute target async function
            result = await func(*args, **kwargs)

            # 3.4 Validate return value if requested
            if validate and return_rule is not None:
                return_rule.validate(result, value_name="return value", context=context)

            # 3.5 Return validated result
            return result

        return wrapper

    # 4. Plain synchronous wrapper
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

        # 4.1 Bind call arguments to signature
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        validate = should_validate(bound, has_bypass=has_bypass)

        # 4.2 Validate arguments against parameter rules
        if validate:
            for name, value in bound.arguments.items():
                rule = compiled.get(name)
                if rule is not None:
                    rule.validate(value, value_name=name, context=context)

        # 4.3 Execute target function
        result = func(*args, **kwargs)

        # 4.4 Validate return value if requested
        if validate and return_rule is not None:
            return_rule.validate(result, value_name="return value", context=context)

        # 4.5 Return validated result
        return result

    return wrapper


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
closure that calls into both. See each helper's own design notes for its
specific rationale; both exist as separate functions (rather than one
combined helper) because they operate on structurally different inputs
(a dict of parameters vs. a single return annotation) and have
independent, differently-shaped return types (`dict[str, Rule]` vs.
`Rule | None`).

---

## 3. Compilation Happens Once, at Decoration Time

Every helper (`compile_parameter_rules`, `compile_return_rule`, and the
`has_bypass` check) runs exactly once, when `@validate_call` is applied
to a function — never per call. `wrapper` only ever looks up already-built
Rule instances, checks the precomputed `has_bypass` flag, and calls
`.validate()` on what it finds. This mirrors IsTyping's own "decompose
once in __init__, delegate on every is_valid()" principle, applied one
level up.

---

## 4. `bound.apply_defaults()` — Defaults Are Validated Too

Without this, a parameter left at its default value would never appear
in `bound.arguments` and would silently skip validation — including
cases where the default itself violates the parameter's own annotation.
Applying defaults first ensures every parameter with a compiled rule is
actually checked, regardless of whether the caller supplied it explicitly.
This also matters for the bypass parameter itself (section 8 below):
`should_validate` reads its value out of `bound.arguments`, which is only
guaranteed to hold an entry for it — even when the caller didn't pass it
explicitly — because defaults were already applied.

---

## 5. Return-Value Validation Is Opt-In, and Symmetric With `check`'s Guard

`check_return` defaults to False — many functions have return annotations
that are more aspirational/documentary than parameter annotations tend to
be, and turning this on unconditionally would silently start enforcing
constraints on existing, already-annotated functions that never asked
for it. When explicitly requested but no return annotation exists,
compile_return_rule raises at decoration time — the same "explicit
request without a rule source is always an error" principle
compile_parameter_rules applies to `check` on the parameter side, kept
symmetric here on the return side.

---

## 6. `@overload` for Full Signature-Preserving Type Hints

Two `@overload` signatures precede the real implementation: one for bare
`@validate_call` (returns `Callable[P, R]` — the exact original
signature, unchanged), one for `@validate_call(...)` with keyword
arguments (returns a decorator producing `Callable[P, R]`). Neither
overload body ever executes — Python ignores `@overload`-decorated
bodies entirely at runtime; only the final, undecorated implementation
below them actually runs. `ParamSpec` (P) captures the decorated
function's exact parameter list and carries it through to the wrapped
result, so IDEs/mypy see the decorated function's real signature.
Requires Python 3.10+ (`ParamSpec` was added to `typing` in 3.10).

---

## 7. Async Functions Get Their Own Wrapper Branch

Parameter validation itself never needs to be async — every argument is
known before the call starts, so validating it synchronously, before
`func` even runs, is the correct fail-fast behavior regardless of whether
`func` is a coroutine function. This is a permanent property of
validation itself, not just a detail of this decorator: `Rule.is_valid()`
is a pure CPU computation (comparisons, isinstance checks, iteration) —
it never waits on anything external, so there is nothing for `async`/
`await` to usefully express there, in any part of this library.

What *does* differ for a coroutine function is how its **result** is
obtained: calling an `async def` function synchronously returns an
unstarted coroutine object, not its eventual result. That bare object
would never satisfy `return_rule` (it isn't the value the caller actually
gets), and `check_return=True` would reject essentially any coroutine
outright regardless of what it would have resolved to.
`inspect.iscoroutinefunction(func)`, checked once at decoration time,
selects an `async def wrapper` that awaits `func(...)` before validating
its result — parameter validation is identical and unchanged in both
branches; only how the return value is obtained and subsequently checked
differs. This mirrors log_this's identical sync/async branching (see its
own design notes) and cannot be unified for the same reason: sharing the
`await` would force the sync branch to become async too, breaking plain
synchronous callers who never asked to await anything.

---

## 8. The Per-Call Bypass Switch: One Decorator, Not Two

A function may opt in to a reserved "validate" bypass parameter (see
is_bypass_parameter's own design notes for its detection rules) — when
present, its value at call time (via `should_validate`) gates both
parameter and return-value checks for that one call. `has_bypass` is
computed once per decoration (a single pass over `signature.parameters`,
no more expensive than the pass compile_parameter_rules already makes),
and `should_validate` itself is a single, cheap boolean check per call
for functions that don't opt in (`if not has_bypass: return True` — no
dict lookup, no extra work). This cost was weighed against splitting
this decorator into two (one plain, one bypass-aware): a second,
near-identical implementation would need to track every future change to
this file in lockstep (the async branch, `check`/`overrides`/
`check_return` handling, the `@overload` pair) purely to save a single
`if` per call that the runtime cost of `inspect.Signature.bind()` alone
already dwarfs. One decorator that silently does nothing extra for
functions without a bypass parameter, and gates exactly two operations
for functions that opt in, was judged the better trade — no drift risk,
no extra decision for callers to make about which decorator to reach for.

`is_bypass_parameter` deliberately does not *require* a function to have
a "validate" parameter — bypass support is opt-in per function, detected
structurally (name + bool-or-unannotated type), never enforced. Requiring
it would tie a specific parameter name to this decorator's behavior
unconditionally, which is exactly the kind of implicit, guessed-at
convention this library avoids elsewhere (see override_rules' own
rejection of a similarly implicit tuple-vs-single-rule guess).

---

## 9. Naming: the Local `validate` Variable

Inside each wrapper, the boolean result of `should_validate(...)` is
bound to a local variable literally named `validate` — matching
`BYPASS_PARAM_NAME`'s value, but not referencing anything by that name:
no `validate()` function is imported into this module, so this is purely
a local, per-call flag chosen to read naturally at each call site
(`if validate: ...`, `if validate and return_rule is not None: ...|`),
mirroring the parameter name a decorated function would use for the same
concept in its own signature.
"""