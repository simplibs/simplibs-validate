import functools
import inspect
import logging
import time
from typing import Callable, ParamSpec, TypeVar, overload
# Inners
from ._helpers import (
    format_bound_arguments,
    log_start,
    log_success,
    log_exception,
    get_context_info
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
    log_exceptions: bool = True,
    logger: logging.Logger | None = None,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Give any function call/entry/exit/exception logging, without imposing
    any logging configuration of its own.

    Every log record is emitted through logging.getLogger(func.__module__)
    — the decorated function's own module logger — so it integrates with
    whatever logging setup the caller's application already has. This
    decorator never calls logging.basicConfig() or attaches any handler.

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
        log_exceptions: If True, an exception raised by the wrapped
            function is logged at ERROR (with traceback) before being
            re-raised unchanged — never swallowed.
        logger: Overrides the automatically derived
            logging.getLogger(func.__module__) logger.

    Returns:
        The wrapped function, logging on every call.
    """
    # 1. Support both @log_this and @log_this(...)
    if func is None:
        return lambda f: log_this(
            f,
            level=level,
            exclude=exclude,
            log_result=log_result,
            log_exceptions=log_exceptions,
            logger=logger,
        )

    # 2. Resolved once, at decoration time
    signature = inspect.signature(func)
    context_info = get_context_info(func)
    active_logger = logger or logging.getLogger(context_info["module"] or "unknown")
    func_name = context_info["name"]

    # 3. Async functions need an async wrapper — timing/logging must wrap the actual await, not just coroutine creation.
    # This cannot be unified with the sync branch below — see this module's design notes, section 1.
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            # 3.1 Bind arguments and format call signature
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            call_repr = format_bound_arguments(bound, exclude=exclude)

            # 3.2 Log start of execution
            log_start(active_logger, level, func_name, call_repr)
            started = time.perf_counter()

            # 3.3 Execute target async function and log potential exception
            try:
                result = await func(*args, **kwargs)
            except Exception:
                log_exception(active_logger, log_exceptions, func_name, call_repr, started)
                raise

            # 3.4 Log successful execution result
            log_success(active_logger, level, func_name, call_repr, started, result, log_result)

            # 3.5 Return execution result
            return result

        return wrapper

    # 4. Plain synchronous wrapper
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

        # 4.1 Bind arguments and format call signature
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        call_repr = format_bound_arguments(bound, exclude=exclude)

        # 4.2 Log start of execution
        log_start(active_logger, level, func_name, call_repr)
        started = time.perf_counter()

        # 4.3 Execute target function and log potential exception
        try:
            result = func(*args, **kwargs)
        except Exception:
            log_exception(active_logger, log_exceptions, func_name, call_repr, started)
            raise

        # 4.4 Log successful execution result
        log_success(active_logger, level, func_name, call_repr, started, result, log_result)

        # 4.5 Return execution result
        return result

    return wrapper


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
func(...)` vs. `result = await func(...)` — but that single `await` is
why they cannot be merged into one shared function. Any function
containing `await` must itself be `async def`; sharing that one line
would force the sync branch to either become async itself (breaking
plain synchronous callers, who would suddenly need to await a function
that was never async to begin with) or spin up an event loop internally
just to call one helper — both worse than the current, admittedly
near-identical, two-branch duplication. What *can* and does live in one
shared place is every individual logging step around that line — see
_helpers/ (log_start, log_success, log_exception,
format_bound_arguments), which both branches call identically.

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

## 5. No Special-Casing of "Falsy" Results

A returned `False`/`None`/`0`/empty value is logged the same as any other
successful result — see log_success's own design notes for the full
rationale, particularly relevant given simplibs-validate's own
`return_bool=True` convention.

---

## 6. What This Deliberately Does Not Do

* No log formatting/handler/destination configuration.
* No automatic detection of "password-looking" parameter names — only
  the explicit `exclude` tuple masks anything.
* No result truncation for large return values — `log_result=False` is
  the escape hatch.
"""