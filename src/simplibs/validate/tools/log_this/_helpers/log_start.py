import logging


def log_start(
    logger: logging.Logger,
    level: int,
    func_name: str,
    call_repr: str,
) -> None:
    """Log a function call's entry, before it runs.

    Args:
        logger: The logger to emit through — the decorated function's own
            module logger (or an explicit override).
        level: Log level to emit at.
        func_name: The pre-extracted function name (e.g. qualified name).
        call_repr: The pre-formatted "name=value, ..." call signature.
    """
    logger.log(level, "Calling %s(%s)", func_name, call_repr)


_DESIGN_NOTES = """
# log_start — log_this's Entry-Point Logger

## Purpose
Emits the single "this call is starting" log record shared identically
by both log_this's sync and async wrapper branches — see log_this.py's
own design notes for why those two branches cannot otherwise share their
surrounding control flow.

---

## 1. No Timing Here

Timing starts in the wrapper itself (`time.perf_counter()`), immediately
after this call, not inside it — keeping "log that we started" and "start
the clock" as two separate, individually obvious statements in the
wrapper's own body, rather than smuggling a side effect (returning a
start time) out of a function whose name only promises logging.
"""