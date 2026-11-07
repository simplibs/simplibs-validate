import inspect
from collections.abc import Iterator


def materialize_iterator_arguments(
    bound: inspect.BoundArguments,
    names: tuple[str, ...],
) -> bool:
    """Replace one-shot iterators among the named arguments with tuples.

    Mutates `bound.arguments` in place, so both validation and the final
    call see the same, re-iterable tuple.

    Args:
        bound: This call's bound arguments.
        names: Parameter names eligible for conversion
            (see find_iterable_parameters).

    Returns:
        True if at least one argument was converted, otherwise False.
    """

    changed = False
    for name in names:
        value = bound.arguments.get(name)

        # 1. Only one-shot iterators are converted — lists, sets, ... stay as they are
        if isinstance(value, Iterator):
            bound.arguments[name] = tuple(value)
            changed = True

    return changed


_DESIGN_NOTES = """
# materialize_iterator_arguments — Call-Time Iterator-to-Tuple Conversion

## Purpose
The opt-in alternative to rejecting `Iterable[T]` one-shot iterators: the
iterator is consumed exactly once, here, and replaced by a tuple that both
validation and the decorated function then receive.

---

## 1. Only Iterators Are Touched

The test is `isinstance(value, Iterator)` — the same definition IsReiterable
uses for "one-shot". Lists, sets, ranges, dict views, ... are left as they
are, so their type and identity reach the function unchanged.

---

## 2. Return Value Tells the Caller Whether to Rebuild the Call

The wrapper calls the function with `bound.args` / `bound.kwargs` only when
something was converted; otherwise it keeps passing the original
`args` / `kwargs`, so calls without iterators behave exactly as before.

---

## 3. Caveat

An infinite generator never finishes and a huge one fills memory. That is
inherent in "convert to tuple" and is the user's conscious choice when
switching the flag on.
"""
