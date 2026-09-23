import logging
import time


def log_exception(
    logger: logging.Logger,
    log_exceptions: bool,
    func_name: str,
    call_repr: str,
    started: float,
) -> None:
    """Log a function call's failure, if enabled. Never suppresses the exception.

    Must be called from inside an `except` block — relies on the
    exception currently being handled to supply exc_info, exactly like
    any ordinary `logger.exception(...)`/`logger.error(..., exc_info=True)`
    call would.

    Args:
        logger: The logger to emit through.
        log_exceptions: If False, this function does nothing — exception
            logging was opted out of.
        func_name: The pre-extracted function name (e.g. qualified name).
        call_repr: The pre-formatted "name=value, ..." call signature.
        started: The time.perf_counter() value captured right before the
            call began — used to compute elapsed time up to the failure.
    """
    if not log_exceptions:
        return

    elapsed = time.perf_counter() - started
    logger.error(
        "%s(%s) raised after %.4fs",
        func_name, call_repr, elapsed,
        exc_info=True,
    )


_DESIGN_NOTES = """
# log_exception — log_this's Failure Logger

## Purpose
Emits the "this call raised" log record shared identically by both
log_this's sync and async wrapper branches. Always called from inside
the wrapper's own `except Exception:` block, immediately before a bare
`raise` re-raises the same exception unchanged — this function never
swallows anything itself; see log_this.py's own design notes, section 4.

---

## 1. `exc_info=True`, Not Manual Traceback Formatting

Relies entirely on Python's own logging machinery to capture and format
the currently-handled exception's traceback — consistent with this
package's stance (see log_this.py's design notes) of never reimplementing
what the standard logging module already does well.

---

## 2. `log_exceptions=False` Means This Function Is a No-Op, Not Skipped by the Caller

The guard lives inside this function rather than at every call site —
both wrapper branches call log_exception unconditionally, and the
decision of whether anything actually gets logged is made once, here.
This keeps the "should we log exceptions" question answered in exactly
one place, rather than duplicated as an `if log_exceptions:` check in
both the sync and async wrapper bodies.
"""