from inspect import BoundArguments


def format_bound_arguments(
    bound: BoundArguments,
    *,
    exclude: tuple[str, ...]
) -> str:
    """Format bound call arguments as a readable, maskable "key=value, ..." string.

    Args:
        bound: The function call's bound arguments (defaults already applied).
        exclude: Parameter names whose value is replaced with a "***" mask
            instead of its repr — for secrets that must never reach a log.

    Returns:
        A single string like "name='chris', age=30, password=***", in
        declaration order, suitable for embedding directly into a log
        message.
    """
    # 1. One "name=repr" (or "name=***") fragment per bound parameter
    parts = [
        f"{name}=***" if name in exclude else f"{name}={value!r}"
        for name, value in bound.arguments.items()
    ]

    # 2. Join into the final call-signature-shaped string
    return ", ".join(parts)


_DESIGN_NOTES = """
# format_bound_arguments — log_this's Call-Signature Formatter

## Purpose
Turns an inspect.BoundArguments (already carrying applied defaults) into
a single readable string suitable for embedding in a log message —
log_this's equivalent of "what did this call look like".

---

## 1. Masking Happens Here, Not as a Filter Bolted Onto logging Itself

`exclude` is checked per-parameter-name during formatting, replacing the
value with a fixed `***` before it ever becomes part of a string. This
guarantees a masked parameter's actual value never touches any log
handler, anywhere, rather than relying on a downstream logging filter to
scrub it after the fact.

---

## 2. `repr()`, Not `str()`

`repr(value)` is used for every non-masked value, matching Python's own
convention for debug-oriented output — the same choice ValidationError's
own diagnostic cards make when displaying a failing value.

---

## 3. *args / **kwargs Show Up As Themselves

BoundArguments already collects a function's `*args`/`**kwargs`
parameters into a tuple/dict under their own parameter name — no
special-casing was needed here; they format through the same
`{name}={value!r}` path as any other parameter.
"""