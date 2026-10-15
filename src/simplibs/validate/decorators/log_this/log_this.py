import functools
import inspect
import logging
import time
from typing import Callable, ParamSpec, TypeVar, overload
# Inners
from ._helpers import (
    build_repr_func,
    format_bound_arguments,
    get_context_info,
    log_exception,
    log_start,
    log_success,
    unwrap_log_this,
)
# Annotations
P = ParamSpec("P")
R = TypeVar("R")


# ============================================================================
# Typing overloads — resolved at type-check time only, never executed.
# See validate_call's own design notes for the general rationale; mirrored
# here identically.
# ============================================================================

@overload
def log_this(func: Callable[P, R]) -> Callable[P, R]: ...


@overload
def log_this(
    func: None = None,
    *,
    level: int = logging.DEBUG,
    exclude: tuple[str, ...] = (),
    log_result: bool = True,
    max_items: int | None = 10,
    log_exceptions: bool = True,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


# ============================================================================
# Actual implementation
# ============================================================================

def log_this(
    func: Callable[P, R] | None = None,
    *,
    level: int = logging.DEBUG,
    exclude: tuple[str, ...] = (),
    log_result: bool = True,
    max_items: int | None = 10,
    log_exceptions: bool = True,
    logger: logging.Logger | None = None,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Give any function call/entry/exit/exception logging, without imposing
    any logging configuration of its own.

    Every log record is emitted through logging.getLogger(func.__module__)
    — the decorated function's own module logger — so it integrates with
    whatever logging setup the caller's application already has. This
    decorator never calls logging.basicConfig() or attaches any handler.

    Large arguments and results are shortened by default (see `max_items`),
    so decorating a function that handles big collections never produces a
    giant log line. When the entry/success level is disabled, nothing is
    formatted unless the call actually raises.

    Works identically on `async def` functions: entry/exit/timing wraps
    around the actual `await`, not just coroutine creation.

    Args:
        func: The function to wrap. Omit when using `@log_this(...)` with
            keyword arguments; present when used as bare `@log_this`.
        level: Log level for the entry/success records. Defaults to
            DEBUG — a successful call is a debugging detail, not an
            application event, unless the caller says otherwise.
        exclude: Parameter names masked (as "***") in the logged call
            signature — for secrets that must never reach a log file.
        log_result: If False, the return value is never included in the
            log record (entry/timing/exceptions are still logged).
        max_items: Maximum number of items shown per container in logged
            arguments and the result (default 10). A shortened container
            also states its total size, e.g. `[a, b, ...] (48213 items)`.
            Long strings and objects are cut at 200 characters. `None`
            disables shortening (full repr).
        log_exceptions: If True, an exception raised by the wrapped
            function is logged at ERROR (with traceback) before being
            re-raised unchanged — never swallowed.
        logger: Overrides the automatically derived
            logging.getLogger(func.__module__) logger.

    Returns:
        The wrapped function, logging on every call.

    Raises:
        ParamError: If `max_items` is neither `None` nor a positive integer
            (raised when the decorator is applied, not on first call).
    """

    # 1. Support both @log_this and @log_this(...) syntax forms
    if func is None:
        return lambda f: log_this(
            f,
            level=level,
            exclude=exclude,
            log_result=log_result,
            max_items=max_items,
            log_exceptions=log_exceptions,
            logger=logger,
        )

    # 2. Peel off existing @log_this wrappers to prevent double logging
    raw_func = unwrap_log_this(func)

    # 3. Resolve function metadata, signature, logger and repr function once at decoration time
    signature = inspect.signature(raw_func)
    context_info = get_context_info(raw_func)
    active_logger = logger or logging.getLogger(context_info["module"] or "unknown")
    func_name = context_info["name"]
    repr_func = build_repr_func(max_items)

    # 4. Shared by both wrappers: render the call signature of one concrete call
    def render_call(args: tuple, kwargs: dict) -> str:
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return format_bound_arguments(bound, exclude=exclude, repr_func=repr_func)

    # 5. Shared by both wrappers: render the signature for a failure record. Runs inside
    #    an `except` block, so it must never raise — a TypeError from a wrong call would
    #    otherwise replace the original exception.
    def render_call_safely(args: tuple, kwargs: dict) -> str:
        try:
            return render_call(args, kwargs)
        except Exception:
            return "<arguments unavailable>"

    # 6. Async functions need an async wrapper — timing/logging must wrap the actual await,
    #    not just coroutine creation. Cannot be unified with the sync branch below.
    if inspect.iscoroutinefunction(raw_func):

        @functools.wraps(raw_func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            # 6.1 Fast path — nothing would be logged, so format nothing
            log_on = active_logger.isEnabledFor(level)
            error_on = log_exceptions and active_logger.isEnabledFor(logging.ERROR)
            if not (log_on or error_on):
                return await raw_func(*args, **kwargs)

            # 6.2 Format and log the entry record (only when its level is enabled)
            call_repr = None
            if log_on:
                call_repr = render_call(args, kwargs)
                log_start(active_logger, level, func_name, call_repr)
            started = time.perf_counter()

            # 6.3 Execute target async function and log potential exception
            try:
                result = await raw_func(*args, **kwargs)
            except Exception:
                if call_repr is None:
                    call_repr = render_call_safely(args, kwargs)
                log_exception(active_logger, log_exceptions, func_name, call_repr, started)
                raise

            # 6.4 Log successful execution result
            if log_on:
                log_success(
                    active_logger, level, func_name, call_repr, started, result, log_result, repr_func,
                )

            # 6.5 Return execution result
            return result

        # 6.6 Mark wrapper for future unwrap inspection
        async_wrapper._is_log_this_wrapper = True  # type: ignore[attr-defined]
        return async_wrapper

    # 7. Plain synchronous wrapper
    @functools.wraps(raw_func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

        # 7.1 Fast path — nothing would be logged, so format nothing
        log_on = active_logger.isEnabledFor(level)
        error_on = log_exceptions and active_logger.isEnabledFor(logging.ERROR)
        if not (log_on or error_on):
            return raw_func(*args, **kwargs)

        # 7.2 Format and log the entry record (only when its level is enabled)
        call_repr = None
        if log_on:
            call_repr = render_call(args, kwargs)
            log_start(active_logger, level, func_name, call_repr)
        started = time.perf_counter()

        # 7.3 Execute target function and log potential exception
        try:
            result = raw_func(*args, **kwargs)
        except Exception:
            if call_repr is None:
                call_repr = render_call_safely(args, kwargs)
            log_exception(active_logger, log_exceptions, func_name, call_repr, started)
            raise

        # 7.4 Log successful execution result
        if log_on:
            log_success(
                active_logger, level, func_name, call_repr, started, result, log_result, repr_func,
            )

        # 7.5 Return execution result
        return result

    # 7.6 Mark wrapper for future unwrap inspection
    sync_wrapper._is_log_this_wrapper = True  # type: ignore[attr-defined]
    return sync_wrapper


_DESIGN_NOTES = """
# log_this — Annotation-Free Call/Entry/Exit/Exception Logger

## Purpose
Gives any function entry, exit, timing, and exception logging without
requiring the function to have any logging code of its own, and without
choosing where those logs end up — that remains entirely the host
application's own logging configuration.

---

## 1. Why Sync and Async Wrappers Cannot Share Their Control Flow

The two wrapper branches differ in exactly one place — `result =
raw_func(...)` vs. `result = await raw_func(...)` — but that single `await` is
why they cannot be merged into one shared function. Any function
containing `await` must itself be `async def`; sharing that one line
would force the sync branch to either become async itself (breaking
plain synchronous callers, who would suddenly need to await a function
that was never async to begin with) or spin up an event loop internally
just to call one helper — both worse than the current, admittedly
near-identical, two-branch duplication. What *can* and does live in one
shared place is every individual logging step around that line — see
_helpers/ (log_start, log_success, log_exception,
format_bound_arguments, build_repr_func), which both branches call identically.

---

## 2. Logger Is Derived From the Decorated Function's Own Module

`logging.getLogger(func.__module__)` — never a simplibs-specific logger
name — so log records from a decorated function in `myapp/services.py`
appear under the `myapp.services` logger, exactly as if the application's
own code had called `logging.getLogger(__name__)` itself.

---

## 3. `level` Defaults to DEBUG, Not INFO

A successful call is a debugging detail — useful when tracing what a
program did, but not, on its own, an application-level event worth
surfacing by default. Callers who want call-level logging visible at
INFO in production pass `level=logging.INFO` explicitly.

---

## 4. Exceptions Are Logged, Never Swallowed

`log_exceptions=True` (default) logs the exception at ERROR with a full
traceback, then unconditionally re-raises via a bare `raise` — the
caller's own exception handling is completely unaffected by this
decorator's presence.

---

## 5. Unwrapping and Wrapper Marking (`_is_log_this_wrapper`)

Before wrapping, `log_this` invokes `unwrap_log_this` to peel away any prior
`@log_this` wrapper layers, preventing duplicate log records or stacked timers.
Both returned wrappers attach `_is_log_this_wrapper = True`, allowing clean,
selective unwrapping without stripping third-party or user decorators.

---

## 6. No Special-Casing of "Falsy" Results

A returned `False`/`None`/`0`/empty value is logged the same as any other
successful result — see log_success's own design notes for the full
rationale, particularly relevant given simplibs-validate's own
`return_bool=True` convention.

---

## 7. Large Values Are Shortened By Default (`max_items`)

Logging must never be the reason a function becomes slow or a log file
huge: a function receiving or returning a list of 50 000 paths would
otherwise write all of them on every call. `max_items=10` (default) shows
at most 10 items per container — nested ones included — and states the
total (`[a, b, ...] (48213 items)`); strings and other objects are cut at
200 characters, so ordinary values (paths, short strings) are never
touched. The shortening uses reprlib, which stops after N items instead
of building the full text first — see build_repr_func's own design notes.

`max_items=None` restores the full repr. The default being a limit rather
than "no limit" is deliberate: a log that cannot be broken by one large
input is the safe default; the rare caller who wants everything asks for it.

`exclude` and `log_result=False` remain the tools for *sensitive* values;
`max_items` is only about size.

---

## 8. Nothing Is Formatted When Nothing Would Be Logged

Both wrappers first ask the logger whether the entry/success level
(`isEnabledFor(level)`) or, with `log_exceptions=True`, ERROR is enabled.
If neither is, the wrapped function is called directly — no argument
binding, no repr, no timing.

The usual production state is "DEBUG off, ERROR on". There the wrapper only
times the call, and the call signature is formatted *lazily*: only if the
call actually raises, inside the failure record. A successful call therefore
costs a few level checks and two clock reads, however large its arguments.

The price of that laziness: a failure record describes the arguments as they
are when the exception is caught, so an argument the function mutated in
place shows its mutated state. When the entry level is enabled the signature
is formatted before the call, i.e. exactly as it was at entry. Formatting a
failure record never raises — if the arguments cannot be rendered (e.g. the
exception was the TypeError of a wrong call), `<arguments unavailable>`
is logged and the original exception propagates untouched.

---

## 9. What This Deliberately Does Not Do

* No log formatting/handler/destination configuration.
* No automatic detection of "password-looking" parameter names — only
  the explicit `exclude` tuple masks anything.
* No separate limits for arguments vs. result, or for strings vs.
  containers — one number (`max_items`) is the whole knob. `None` is the
  escape hatch.
"""
