import reprlib
from collections import deque
from itertools import islice
from typing import Any, Callable
# Outers
from .._validations import raise_invalid_max_items

# Exact builtin container types that get an item limit and a total count.
# Subclasses (defaultdict, namedtuple, ...) fall through to reprlib's generic
# "other object" path, which is length-limited by `maxother`.
_CONTAINERS = (list, tuple, set, frozenset, dict, deque)

# Generous character limits: a path or a short string must never be cut
# in the middle, only genuinely huge values are shortened.
_MAX_TEXT = 200


def _safe_repr(value: Any) -> str:
    """Plain `repr`, which can never break the decorated call."""
    try:
        return repr(value)
    except Exception:
        return f"<{type(value).__name__} (repr failed)>"


class _LimitedRepr(reprlib.Repr):
    """`reprlib.Repr` limited to `max_items` items per container, which also
    states the total size of every container it had to shorten."""

    def __init__(self, max_items: int) -> None:
        super().__init__()
        self.maxlist = self.maxtuple = self.maxset = self.maxfrozenset = max_items
        self.maxdict = self.maxdeque = self.maxarray = max_items
        self.maxstring = self.maxother = _MAX_TEXT
        self.maxlong = _MAX_TEXT
        self._max_items = max_items

    def repr1(self, x: Any, level: int) -> str:
        kind = type(x)
        if kind not in _CONTAINERS or len(x) <= self._max_items:
            return super().repr1(x, level)

        total = len(x)

        # reprlib sorts a whole set/dict before cutting it — hand it a small
        # slice instead (one item over the limit, so it still prints "...").
        if kind in (set, frozenset):
            x = kind(islice(x, self._max_items + 1))
        elif kind is dict:
            x = dict(islice(x.items(), self._max_items + 1))

        return f"{super().repr1(x, level)} ({total} items)"


def build_repr_func(max_items: int | None) -> Callable[[Any], str]:
    """Build the `value -> str` function `log_this` uses for every logged
    argument and result.

    Args:
        max_items: Maximum number of items shown per container (nested ones
            included). `None` disables shortening and gives a plain, safe
            `repr`.

    Returns:
        A function returning a bounded (or plain) `repr` of any value.

    Raises:
        ParamError: If `max_items` is neither `None` nor a positive integer.
    """

    # 1. No limit requested: plain repr
    if max_items is None:
        return _safe_repr

    # 2. Reject anything that is not a positive int (bool is an int subclass)
    if isinstance(max_items, bool) or not isinstance(max_items, int) or max_items < 1:
        raise_invalid_max_items(max_items)

    # 3. Limited repr
    return _LimitedRepr(max_items).repr


_DESIGN_NOTES = """
# build_repr_func — bounded repr for log_this

## Purpose
Gives log_this one `value -> str` function, built once at decoration time,
used for both the logged arguments and the logged result.

## Why reprlib, not "repr() and cut the string"
`repr(big_list)` builds the whole string first and only then could be cut —
the cost log_this wants to avoid. reprlib stops after N items, so a list of
50 000 paths costs the same as a list of 10.

## Why the total count
`[a, b, ...]` says nothing about whether 11 or 48 213 items were cut.
"(48213 items)" is what a log reader actually needs.

## Why sets and dicts are pre-sliced
reprlib sorts the *whole* set/dict before cutting it. Passing it a slice of
`max_items + 1` elements keeps it cheap and still prints "...".

## Why 200 characters for strings/other objects
reprlib's defaults (30 / 30) cut a normal `PosixPath('/home/me/project/x.py')`
in half. 200 only touches genuinely huge values.

## `max_items=None`
Plain repr (guarded, so a broken `__repr__` cannot break the decorated call).
reprlib's own instance path already catches failing `__repr__`.
"""
