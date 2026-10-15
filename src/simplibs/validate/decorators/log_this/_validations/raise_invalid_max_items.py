from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_invalid_max_items(
    max_items: Any
) -> NoReturn:
    """Raise a ParamError when log_this receives an unusable `max_items`.

    Args:
        max_items: The rejected value — anything that is neither `None` nor a
            positive integer (a bool is rejected too).

    Raises:
        ParamError: Always.
    """
    raise ParamError(
        error_name="LOG_THIS_INVALID_MAX_ITEMS_ERROR",
        label="max_items",
        expected="None (no shortening) or a positive integer.",
        value=max_items,
        problem=(
            f"Option 'max_items={max_items!r}' of log_this() is not valid.",
            "It must be None or a positive integer: the number of items shown per container.",
        ),
        how_to_fix=(
            "Pass a positive integer, e.g. max_items=10.",
            "Pass max_items=None to log arguments and results in full.",
        ),
    )


_DESIGN_NOTES = """
# raise_invalid_max_items — log_this Diagnostic Helper

## Purpose
Single point of failure for an unusable `max_items`. Raised when `log_this` is
applied to a function (not on its first call), so the mistake surfaces at import
time. A ParamError, like every other decoration-time configuration mistake in this
package (see raise_no_rule_for_checked_param / raise_no_rule_for_return), instead of
a bare built-in ValueError.

## Why a bool Is Rejected
`True` is an `int`, so `max_items=True` would otherwise silently mean "show 1 item".
That is almost certainly a mistake, so it is reported like any other invalid value.
"""
