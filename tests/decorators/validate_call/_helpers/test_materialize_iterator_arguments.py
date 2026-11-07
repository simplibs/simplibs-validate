import inspect

# Tested helper
from simplibs.validate.decorators.validate_call._helpers.materialize_iterator_arguments import (
    materialize_iterator_arguments,
)


def func(xs, ys=None, *, zs=None): ...


def _bind(*args, **kwargs) -> inspect.BoundArguments:
    """Bind arguments to the sample signature."""
    return inspect.signature(func).bind(*args, **kwargs)


# ============================================================================
# Conversion
# ============================================================================

def test_materialize_iterator_arguments_converts_generator() -> None:
    """Verify a generator is replaced by a tuple with all of its items, in order."""
    bound = _bind(x for x in range(4))

    assert materialize_iterator_arguments(bound, ("xs",)) is True
    assert bound.arguments["xs"] == (0, 1, 2, 3)
    assert isinstance(bound.arguments["xs"], tuple)


def test_materialize_iterator_arguments_converts_plain_iterator() -> None:
    """Verify iter(...) and map(...) objects are converted too."""
    bound = _bind(iter([1, 2]), ys=map(str, [3, 4]))

    assert materialize_iterator_arguments(bound, ("xs", "ys")) is True
    assert bound.arguments["xs"] == (1, 2)
    assert bound.arguments["ys"] == ("3", "4")


def test_materialize_iterator_arguments_converts_keyword_only() -> None:
    """Verify keyword-only arguments are converted."""
    bound = _bind([1], zs=iter([5, 6]))

    assert materialize_iterator_arguments(bound, ("zs",)) is True
    assert bound.arguments["zs"] == (5, 6)


def test_materialize_iterator_arguments_empty_iterator_becomes_empty_tuple() -> None:
    """Verify an empty iterator still counts as a conversion and gives ()."""
    bound = _bind(iter([]))

    assert materialize_iterator_arguments(bound, ("xs",)) is True
    assert bound.arguments["xs"] == ()


# ============================================================================
# Untouched values
# ============================================================================

def test_materialize_iterator_arguments_leaves_reiterable_collections_alone() -> None:
    """Verify list, tuple, set, range and dict keep their identity."""
    values = [1, 2], (1, 2), {1, 2}, range(3), {"a": 1}
    for value in values:
        bound = _bind(value)

        assert materialize_iterator_arguments(bound, ("xs",)) is False
        assert bound.arguments["xs"] is value


def test_materialize_iterator_arguments_leaves_strings_alone() -> None:
    """Verify a string (iterable, but not an iterator) is not converted."""
    bound = _bind("abc")

    assert materialize_iterator_arguments(bound, ("xs",)) is False
    assert bound.arguments["xs"] == "abc"


def test_materialize_iterator_arguments_ignores_names_not_listed() -> None:
    """Verify an iterator under a name that is not eligible stays an iterator."""
    iterator = iter([1, 2])
    bound = _bind([0], ys=iterator)

    assert materialize_iterator_arguments(bound, ("xs",)) is False
    assert bound.arguments["ys"] is iterator


def test_materialize_iterator_arguments_missing_argument_is_not_added() -> None:
    """Verify a listed name that was not passed (and not defaulted) is skipped."""
    bound = _bind([1])

    assert materialize_iterator_arguments(bound, ("ys",)) is False
    assert "ys" not in bound.arguments


def test_materialize_iterator_arguments_no_names_is_noop() -> None:
    """Verify an empty name tuple changes nothing."""
    iterator = iter([1])
    bound = _bind(iterator)

    assert materialize_iterator_arguments(bound, ()) is False
    assert bound.arguments["xs"] is iterator


# ============================================================================
# Mixed
# ============================================================================

def test_materialize_iterator_arguments_converts_only_the_iterators() -> None:
    """Verify the return value is True when at least one argument changed and the rest stays."""
    keep = [1, 2]
    bound = _bind(keep, ys=iter([3]))

    assert materialize_iterator_arguments(bound, ("xs", "ys")) is True
    assert bound.arguments["xs"] is keep
    assert bound.arguments["ys"] == (3,)


def test_materialize_iterator_arguments_result_can_be_iterated_repeatedly() -> None:
    """Verify the produced tuple is re-iterable (the point of the conversion)."""
    bound = _bind(x for x in range(3))
    materialize_iterator_arguments(bound, ("xs",))

    assert list(bound.arguments["xs"]) == [0, 1, 2]
    assert list(bound.arguments["xs"]) == [0, 1, 2]


def test_materialize_iterator_arguments_updates_bound_args_and_kwargs() -> None:
    """Verify bound.args / bound.kwargs (used for the final call) reflect the conversion."""
    bound = _bind(iter([1, 2]), zs=iter([3]))
    materialize_iterator_arguments(bound, ("xs", "zs"))

    assert bound.args == ((1, 2),)
    assert bound.kwargs == {"zs": (3,)}
