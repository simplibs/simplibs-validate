import logging
from collections import deque
from pathlib import PurePosixPath
import pytest

from simplibs.exception import ParamError
from simplibs.validate.decorators.log_this._helpers import build_repr_func


class _BrokenRepr:
    def __repr__(self) -> str:
        raise RuntimeError("repr is broken")


class _CountingRepr:
    """Counts how many times its repr is actually built."""
    calls = 0

    def __repr__(self) -> str:
        type(self).calls += 1
        return "item"


# ============================================================================
# max_items=None — plain, safe repr
# ============================================================================

def test_none_returns_plain_repr() -> None:
    """Verify None disables shortening entirely."""
    repr_func = build_repr_func(None)
    big = list(range(1000))

    assert repr_func([1, 2, 3]) == "[1, 2, 3]"
    assert repr_func(big) == repr(big)


def test_none_survives_broken_repr() -> None:
    """Verify a failing __repr__ never breaks the logged call."""
    repr_func = build_repr_func(None)

    assert repr_func(_BrokenRepr()) == "<_BrokenRepr (repr failed)>"


# ============================================================================
# Validation of max_items
# ============================================================================

@pytest.mark.parametrize("invalid", [0, -1, True, False, "3", 2.5])
def test_invalid_max_items_raises(invalid: object) -> None:
    """Verify anything except None or a positive int is rejected immediately."""
    with pytest.raises(ParamError):
        build_repr_func(invalid)  # type: ignore[arg-type]


# ============================================================================
# Containers
# ============================================================================

def test_container_within_limit_is_untouched() -> None:
    """Verify a container that fits is rendered exactly like repr."""
    repr_func = build_repr_func(10)

    assert repr_func([1, 2, 3]) == "[1, 2, 3]"
    assert repr_func(list(range(10))) == repr(list(range(10)))  # exactly at the limit


def test_list_over_limit_is_shortened_with_total() -> None:
    """Verify a long list shows max_items items plus the total count."""
    assert build_repr_func(3)(list(range(10))) == "[0, 1, 2, ...] (10 items)"


def test_minimal_limit() -> None:
    """Verify max_items=1 still works."""
    assert build_repr_func(1)([1, 2]) == "[1, ...] (2 items)"


def test_tuple_over_limit() -> None:
    """Verify tuples are shortened like lists."""
    assert build_repr_func(2)((1, 2, 3)) == "(1, 2, ...) (3 items)"


def test_deque_over_limit() -> None:
    """Verify deques are shortened."""
    assert build_repr_func(2)(deque([1, 2, 3])) == "deque([1, 2, ...]) (3 items)"


def test_dict_over_limit_keeps_insertion_order() -> None:
    """Verify a long dict shows its first max_items entries plus the total."""
    assert build_repr_func(2)({i: i for i in range(5)}) == "{0: 0, 1: 1, ...} (5 items)"


def test_set_over_limit() -> None:
    """Verify a long set is shortened and reports its total."""
    result = build_repr_func(3)(set(range(100)))

    assert result.startswith("{")
    assert "..." in result
    assert result.endswith("(100 items)")


def test_frozenset_over_limit() -> None:
    """Verify a long frozenset is shortened and reports its total."""
    result = build_repr_func(3)(frozenset(range(100)))

    assert result.startswith("frozenset({")
    assert result.endswith("(100 items)")


def test_nested_containers_are_limited_too() -> None:
    """Verify the limit applies at every nesting level."""
    result = build_repr_func(2)([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    assert result == "[[1, 2, ...] (3 items), [4, 5, ...] (3 items), ...] (3 items)"


def test_only_needed_items_are_rendered() -> None:
    """Verify the full text is never built — items beyond the limit are not repr'd."""
    _CountingRepr.calls = 0

    build_repr_func(3)([_CountingRepr() for _ in range(1000)])

    assert _CountingRepr.calls == 3


# ============================================================================
# Text and other objects
# ============================================================================

def test_short_values_are_untouched() -> None:
    """Verify ordinary strings and paths are never cut."""
    repr_func = build_repr_func(10)
    path = PurePosixPath("/home/me/project/src/pkg/module.py")

    assert repr_func("hello") == "'hello'"
    assert repr_func(path) == repr(path)


def test_long_string_is_cut() -> None:
    """Verify a huge string is shortened."""
    result = build_repr_func(10)("x" * 5000)

    assert len(result) < 300
    assert "..." in result


def test_huge_object_repr_is_cut() -> None:
    """Verify an object with a huge repr is shortened."""
    class Huge:
        def __repr__(self) -> str:
            return "H" * 5000

    result = build_repr_func(10)(Huge())

    assert len(result) < 300
    assert "..." in result


def test_container_subclass_falls_back_to_character_limit() -> None:
    """Verify a list subclass is not item-limited but is still bounded in length."""
    class MyList(list):
        pass

    result = build_repr_func(3)(MyList(range(5000)))

    assert len(result) < 300


def test_broken_repr_inside_limited_repr() -> None:
    """Verify a failing __repr__ cannot break the limited repr either."""
    result = build_repr_func(10)(_BrokenRepr())

    assert result.startswith("<_BrokenRepr instance")


# ============================================================================
# General properties
# ============================================================================

def test_repr_func_is_stateless() -> None:
    """Verify repeated calls give identical results."""
    repr_func = build_repr_func(3)
    data = list(range(10))

    assert repr_func(data) == repr_func(data)
    assert repr_func([1]) == "[1]"
