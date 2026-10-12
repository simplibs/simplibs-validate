import logging
import time
from typing import Any, Callable


def log_success(
    logger: logging.Logger,
    level: int,
    func_name: str,
    call_repr: str,
    started: float,
    result: Any,
    log_result: bool,
    repr_func: Callable[[Any], str] = repr,
) -> None:
    """Log a function call's successful completion, including elapsed time.

    Args:
        logger: The logger to emit through.
        level: Log level to emit at.
        func_name: The pre-extracted function name (e.g. qualified name).
        call_repr: The pre-formatted "name=value, ..." call signature.
        started: The time.perf_counter() value captured right before the
            call began — used to compute elapsed time.
        result: The function's return value. Logged as-is through
            `repr_func`, regardless of what it is (including False/None/0 —
            none of these are treated as failure; see log_this's own design
            notes on why this decorator never special-cases a "falsy"
            result).
        log_result: If False, the result itself is omitted from the log
            message (elapsed time is still logged).
        repr_func: Turns the result into its logged text. Defaults to plain
            `repr`; log_this passes a bounded one so a huge result stays short.
    """
    elapsed = time.perf_counter() - started

    if log_result:
        logger.log(
            level, "%s(%s) returned %s in %.4fs",
            func_name, call_repr, repr_func(result), elapsed,
        )
    else:
        logger.log(
            level, "%s(%s) completed in %.4fs",
            func_name, call_repr, elapsed,
        )


_DESIGN_NOTES = """
# log_success — log_this's Completion Logger

## Purpose
Emits the "this call finished successfully" log record shared identically
by both log_this's sync and async wrapper branches.

---

## 1. No Special-Casing of "Falsy" Results

`result` is logged exactly as returned — `False`, `None`, `0`, an empty
collection, all log the same way as any other value. This decorator has
no concept of "this function's result means failure"; the only
recognized failure signal anywhere in log_this is an actual raised
exception, handled entirely by log_exception instead. A function that
legitimately returns False as a normal outcome (e.g. simplibs-validate's
own `return_bool=True` path) must not be treated as having failed just
because its result happens to be falsy.

---

## 2. `log_result=False` Still Logs Timing

Suppressing the result (for size or sensitivity reasons) does not
suppress the rest of the record — elapsed time and the call signature
are still useful on their own even when the return value itself must
stay out of the log.

---

## 3. The Result Is Rendered Eagerly, Through `repr_func`

Unlike a plain `%r`, the result is converted to text here, before logger.log
is called, because the bounded repr is a separate function. The cost is
paid only when this function is called at all — log_this skips it entirely
when the record's level is disabled (see log_this's design notes, section 8).
"""
