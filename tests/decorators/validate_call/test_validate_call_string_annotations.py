from __future__ import annotations

import inspect
from collections.abc import Iterable
from typing import Annotated, Callable, Literal, Optional

import pytest

# Tested decorator and exceptions
from simplibs.exception import ParamError, ValidationError
from simplibs.rules import greater_than
from simplibs.validate.decorators.validate_call.validate_call import validate_call

# This whole module uses `from __future__ import annotations`, so every
# annotation below is a string until validate_call resolves it.


# ============================================================================
# Names that do not exist yet when the decorator runs (module level)
# ============================================================================

@validate_call
def describe(item: LaterClass) -> str:
    return "ok"


@validate_call
async def describe_async(item: LaterClass) -> str:
    return "ok"


class LaterClass:
    """Defined *after* the functions that are annotated with it."""


class Vector:
    def __init__(self, x: int) -> None:
        self.x = x

    @validate_call
    def add(self, other: Vector) -> Vector:
        return Vector(self.x + other.x)

    @validate_call(check_return=True)
    def wrong_return(self) -> Vector:
        return 5  # type: ignore[return-value]


# ============================================================================
# Plain string annotations
# ============================================================================

def test_validate_call_string_annotations_parameters() -> None:
    """Verify parameters annotated by (future-)strings are validated."""

    @validate_call
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5

    with pytest.raises(ValidationError):
        add(2, "3")


def test_validate_call_string_annotations_return_value() -> None:
    """Verify check_return works with a string return annotation."""

    @validate_call(check_return=True)
    def bad(a: int) -> int:
        return "not an int"  # type: ignore[return-value]

    with pytest.raises(ValidationError):
        bad(1)


def test_validate_call_string_annotations_union_of_two_types() -> None:
    """Verify the original `*param_sources: A | B` use case works with strings."""

    @validate_call
    def count(*param_sources: inspect.Parameter | Callable) -> int:
        return len(param_sources)

    assert count(len, inspect.Parameter("x", inspect.Parameter.POSITIONAL_ONLY)) == 2

    with pytest.raises(ValidationError):
        count(len, 5)


def test_validate_call_string_annotations_var_keyword() -> None:
    """Verify `**kwargs: str` is validated per value under string annotations."""

    @validate_call
    def collect(**options: str) -> dict:
        return options

    assert collect(a="x") == {"a": "x"}

    with pytest.raises(ValidationError):
        collect(a=1)


def test_validate_call_string_annotations_annotated_with_rule() -> None:
    """Verify Annotated[...] carrying a rule survives resolution."""

    @validate_call
    def age(value: Annotated[int, greater_than(0)]) -> int:
        return value

    assert age(5) == 5

    with pytest.raises(ValidationError):
        age(-1)


def test_validate_call_string_annotations_literal_and_optional() -> None:
    """Verify Literal values and Optional are handled."""

    @validate_call
    def pick(mode: Literal["a", "b"], extra: Optional[int] = None) -> str:
        return mode

    assert pick("a") == "a"
    assert pick("b", 3) == "b"

    with pytest.raises(ValidationError):
        pick("c")

    with pytest.raises(ValidationError):
        pick("a", "x")


def test_validate_call_string_annotations_overrides_still_apply() -> None:
    """Verify overrides combine with a string annotation."""

    @validate_call(overrides={"b": greater_than(0)})
    def divide(a: int, b: int) -> float:
        return a / b

    assert divide(10, 2) == 5.0

    with pytest.raises(ValidationError):
        divide(10, -1)


@pytest.mark.asyncio
async def test_validate_call_string_annotations_async() -> None:
    """Verify async functions work with string annotations."""

    @validate_call(check_return=True)
    async def fetch(valid: bool) -> str:
        return "data" if valid else 123  # type: ignore[return-value]

    assert await fetch(True) == "data"

    with pytest.raises(ValidationError):
        await fetch(False)


# ============================================================================
# Iterable[T] — the original edge, now reachable with string annotations
# ============================================================================

def test_validate_call_string_annotations_iterable_rejects_iterator() -> None:
    """Verify Iterable[T] written as a string still rejects a one-shot iterator."""

    @validate_call
    def total(items: Iterable[int]) -> int:
        return sum(items)

    assert total([1, 2]) == 3

    with pytest.raises(ValidationError):
        total(x for x in range(3))


def test_validate_call_string_annotations_materialize_iterators() -> None:
    """Verify materialize_iterators detects Iterable[T] written as a string."""

    @validate_call(materialize_iterators=True)
    def collect(items: Iterable[int]) -> object:
        return items

    assert collect(x for x in range(3)) == (0, 1, 2)


def test_validate_call_string_annotations_materialize_iterators_optional() -> None:
    """Verify `Iterable[int] | None` written as a string is detected."""

    @validate_call(materialize_iterators=True)
    def collect(items: Iterable[int] | None = None) -> object:
        return items

    assert collect(iter([1, 2])) == (1, 2)
    assert collect() is None


@pytest.mark.asyncio
async def test_validate_call_string_annotations_materialize_iterators_async() -> None:
    """Verify conversion works on async functions with string annotations."""

    @validate_call(materialize_iterators=True)
    async def collect(items: Iterable[int]) -> object:
        return items

    assert await collect(iter([1, 2])) == (1, 2)


# ============================================================================
# Names that do not exist yet at decoration time
# ============================================================================

def test_validate_call_forward_reference_to_later_class() -> None:
    """Verify a class defined below the function resolves on the first call."""
    assert describe(LaterClass()) == "ok"

    with pytest.raises(ValidationError):
        describe(5)


@pytest.mark.asyncio
async def test_validate_call_forward_reference_to_later_class_async() -> None:
    """Verify the same for an async function."""
    assert await describe_async(LaterClass()) == "ok"

    with pytest.raises(ValidationError):
        await describe_async(5)


def test_validate_call_method_annotated_with_its_own_class() -> None:
    """Verify a method may name its own class in parameter and return annotations."""
    result = Vector(1).add(Vector(2))

    assert isinstance(result, Vector)
    assert result.x == 3


def test_validate_call_method_with_own_class_validates_argument() -> None:
    """Verify the self-referencing parameter is really checked."""
    with pytest.raises(ValidationError):
        Vector(1).add(5)


def test_validate_call_method_with_own_class_validates_return() -> None:
    """Verify the self-referencing return annotation is really checked."""
    with pytest.raises(ValidationError):
        Vector(1).wrong_return()


def test_validate_call_forward_reference_resolved_state_is_cached() -> None:
    """Verify repeated calls keep working after the first call built the rules."""
    for _ in range(3):
        assert describe(LaterClass()) == "ok"


def test_validate_call_postponed_function_materialize_iterators() -> None:
    """Verify the flag works for a function whose annotations resolve on the first call."""

    @validate_call(materialize_iterators=True)
    def collect(items: Iterable[_InjectedType]) -> object:
        return items

    globals()["_InjectedType"] = int
    try:
        assert collect(iter([1, 2])) == (1, 2)
    finally:
        del globals()["_InjectedType"]


# ============================================================================
# Failures
# ============================================================================

def test_validate_call_unresolvable_name_is_reported_on_first_call() -> None:
    """Verify decoration succeeds and the first call raises a clear ParamError."""

    @validate_call
    def broken(a: DoesNotExistAnywhere) -> None:  # noqa: F821
        return None

    with pytest.raises(ParamError) as exc_info:
        broken(1)

    assert exc_info.value.error_name == "VALIDATE_CALL_UNRESOLVABLE_ANNOTATION_ERROR"


def test_validate_call_unresolvable_name_keeps_failing_until_fixed() -> None:
    """Verify a failed first call is not cached, so the function recovers once the name exists."""

    @validate_call
    def recoverable(a: _LateRecoveryName) -> int:
        return a

    with pytest.raises(ParamError):
        recoverable(1)

    globals()["_LateRecoveryName"] = int
    try:
        assert recoverable(1) == 1
    finally:
        del globals()["_LateRecoveryName"]


def test_validate_call_invalid_annotation_syntax_raises_at_decoration() -> None:
    """Verify an annotation that can never be evaluated fails immediately."""

    with pytest.raises(ParamError) as exc_info:

        @validate_call
        def broken(a: "list[int") -> None:
            return None

    assert exc_info.value.error_name == "VALIDATE_CALL_UNRESOLVABLE_ANNOTATION_ERROR"


def test_validate_call_postponed_function_reports_configuration_errors_on_first_call() -> None:
    """Verify the materialize_iterators guard of a postponed function appears on its first call."""

    @validate_call(materialize_iterators=True)
    def no_iterable(a: _InjectedPlain) -> int:
        return 0

    globals()["_InjectedPlain"] = int
    try:
        with pytest.raises(ParamError) as exc_info:
            no_iterable(1)
    finally:
        del globals()["_InjectedPlain"]

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_ITERABLE_PARAM_ERROR"


def test_validate_call_configuration_errors_stay_early_when_annotations_resolve() -> None:
    """Verify check= naming an unannotated parameter still fails at decoration time."""

    with pytest.raises(ParamError) as exc_info:

        @validate_call(check=("a",))
        def func(a, b: int) -> None:
            return None

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_RULE_FOR_PARAM_ERROR"


def test_validate_call_bypass_switch_with_string_annotations() -> None:
    """Verify the per-call bypass still works when annotations are strings."""

    @validate_call
    def process(data: int, *, _validate_call: bool = True) -> int:
        return data

    assert process(1) == 1
    assert process("x", _validate_call=False) == "x"

    with pytest.raises(ValidationError):
        process("x")
