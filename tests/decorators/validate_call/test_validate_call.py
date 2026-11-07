import inspect
from collections.abc import Iterable
from typing import Callable

import pytest

# Tested decorator and exceptions
from simplibs.exception import ParamError, ValidationError
from simplibs.rules import HasLength, greater_than
from simplibs.validate.decorators.validate_call.validate_call import validate_call


# ============================================================================
# Synchronous Functions Testing
# ============================================================================

def test_validate_call_bare_decorator_success() -> None:
    """Verify bare @validate_call passes valid arguments on sync functions."""

    @validate_call
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5


def test_validate_call_bare_decorator_failure() -> None:
    """Verify bare @validate_call raises ValidationError on invalid arguments."""

    @validate_call
    def add(a: int, b: int) -> int:
        return a + b

    with pytest.raises(ValidationError):
        add(2, "3")


def test_validate_call_with_check_filter() -> None:
    """Verify check parameter restricts validation to specified parameters only."""

    @validate_call(check=("a",))
    def process(a: int, b: str) -> str:
        return f"{a}-{b}"

    # 'a' is validated (int), 'b' is ignored even though it receives invalid type
    assert process(10, 123) == "10-123"

    with pytest.raises(ValidationError):
        process("invalid", "ok")


def test_validate_call_with_overrides() -> None:
    """Verify overrides add custom validation logic to parameters."""

    @validate_call(overrides={"b": greater_than(0)})
    def divide(a: int, b) -> float:
        return a / b

    assert divide(10, 2) == 5.0

    with pytest.raises(ValidationError):
        divide(10, -1)


def test_validate_call_sync_return_validation_success() -> None:
    """Verify check_return=True validates valid return values."""

    @validate_call(check_return=True)
    def greet(name: str) -> str:
        return f"Hello, {name}"

    assert greet("Alice") == "Hello, Alice"


def test_validate_call_sync_return_validation_failure() -> None:
    """Verify check_return=True raises ValidationError on invalid return values."""

    @validate_call(check_return=True)
    def bad_calculator(a: int) -> int:
        return "not an int"  # Type violation

    with pytest.raises(ValidationError):
        bad_calculator(5)


def test_validate_call_check_return_missing_annotation_raises() -> None:
    """Verify ParamError is raised at decoration time when check_return=True lacks return annotation."""

    with pytest.raises(ParamError) as exc_info:

        @validate_call(check_return=True)
        def no_return_annotation(a: int):
            return a

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_RULE_FOR_RETURN_ERROR"


def test_validate_call_per_call_bypass_switch() -> None:
    """Verify reserved '_validate_call' parameter skips validation when set to False."""

    @validate_call
    def process(data: int, *, _validate_call: bool = True) -> int:
        return data

    # Normal execution with validation
    assert process(10) == 10
    with pytest.raises(ValidationError):
        process("not_an_int")

    # Opt-out bypassing validation
    assert process("not_an_int", _validate_call=False) == "not_an_int"


# ============================================================================
# Asynchronous Functions Testing
# ============================================================================

@pytest.mark.asyncio
async def test_validate_call_async_success() -> None:
    """Verify @validate_call works seamlessly on async functions."""

    @validate_call
    async def async_add(a: int, b: int) -> int:
        return a + b

    result = await async_add(5, 5)
    assert result == 10


@pytest.mark.asyncio
async def test_validate_call_async_param_failure() -> None:
    """Verify parameter validation fails before async function execution."""

    @validate_call
    async def async_add(a: int, b: int) -> int:
        return a + b

    with pytest.raises(ValidationError):
        await async_add("invalid", 5)


@pytest.mark.asyncio
async def test_validate_call_async_return_validation() -> None:
    """Verify check_return=True validates awaited return values in async functions."""

    @validate_call(check_return=True)
    async def async_fetch(valid: bool) -> str:
        if valid:
            return "data"
        return 12345

    assert await async_fetch(True) == "data"

    with pytest.raises(ValidationError):
        await async_fetch(False)


@pytest.mark.asyncio
async def test_validate_call_async_bypass_switch() -> None:
    """Verify bypass switch works properly on async functions."""

    @validate_call
    async def async_process(data: int, *, _validate_call: bool = True) -> int:
        return data

    assert await async_process(10) == 10
    assert await async_process("not_an_int", _validate_call=False) == "not_an_int"


def test_validate_call_prevents_double_wrapping() -> None:
    """Verify that decorating a function multiple times with @validate_call unwraps previous layers."""

    @validate_call
    @validate_call
    def add(a: int, b: int) -> int:
        return a + b

    # Funkce by měla bez problémů projít a neprovádět zdvojené vnitřní operace
    assert add(2, 3) == 5
    with pytest.raises(ValidationError):
        add(2, "3")

    # Ověříme, že wrapper má nastavený marker
    assert getattr(add, "_is_validate_call_wrapper", False) is True


def test_validate_call_validates_default_arguments() -> None:
    """Verify bound.apply_defaults() ensures invalid default values trigger ValidationError on call."""

    @validate_call
    def func_with_bad_default(a: int = "invalid_default") -> str:
        return str(a)

    # Volání bez argumentů musí selhat na validaci výchozí hodnoty
    with pytest.raises(ValidationError):
        func_with_bad_default()


# ============================================================================
# Variadic parameters (*args / **kwargs)
# ============================================================================

def test_validate_call_var_positional_success() -> None:
    """Verify `*args: int` validates every item, not the tuple as a whole."""

    @validate_call
    def total(*numbers: int) -> int:
        return sum(numbers)

    assert total(1, 2, 3) == 6


def test_validate_call_var_positional_empty() -> None:
    """Verify calling without any variadic arguments is valid."""

    @validate_call
    def total(*numbers: int) -> int:
        return sum(numbers)

    assert total() == 0


def test_validate_call_var_positional_failure() -> None:
    """Verify one invalid item in `*args` raises ValidationError."""

    @validate_call
    def total(*numbers: int) -> int:
        return sum(numbers)

    with pytest.raises(ValidationError):
        total(1, "2", 3)


def test_validate_call_var_positional_union_annotation() -> None:
    """Verify the natural `*sources: A | B` annotation works without tuple[...] or a bare `*`."""

    @validate_call
    def count(*param_sources: inspect.Parameter | Callable) -> int:
        return len(param_sources)

    parameter = inspect.Parameter("x", inspect.Parameter.POSITIONAL_ONLY)
    assert count(len, parameter) == 2

    with pytest.raises(ValidationError):
        count(len, 5)


def test_validate_call_var_positional_mixed_with_regular_parameters() -> None:
    """Verify regular parameters and `*args` are validated side by side."""

    @validate_call
    def join(sep: str, *parts: str) -> str:
        return sep.join(parts)

    assert join("-", "a", "b") == "a-b"

    with pytest.raises(ValidationError):
        join(1, "a")  # regular parameter fails

    with pytest.raises(ValidationError):
        join("-", "a", 2)  # variadic item fails


def test_validate_call_var_keyword_success() -> None:
    """Verify `**kwargs: int` validates every value."""

    @validate_call
    def collect(**options: int) -> dict:
        return options

    assert collect(a=1, b=2) == {"a": 1, "b": 2}
    assert collect() == {}


def test_validate_call_var_keyword_failure() -> None:
    """Verify one invalid value in `**kwargs` raises ValidationError."""

    @validate_call
    def collect(**options: int) -> dict:
        return options

    with pytest.raises(ValidationError):
        collect(a=1, b="2")


def test_validate_call_var_positional_override_sees_whole_tuple() -> None:
    """Verify an override on `*args` is a collection-level rule (e.g. at least one item)."""

    @validate_call(overrides={"numbers": HasLength(min_length=1)})
    def total(*numbers: int) -> int:
        return sum(numbers)

    assert total(1, 2) == 3

    with pytest.raises(ValidationError):
        total()  # empty tuple violates the override

    with pytest.raises(ValidationError):
        total("x")  # annotation still applies to each item


def test_validate_call_unannotated_variadic_parameters_are_skipped() -> None:
    """Verify unannotated `*args` / `**kwargs` are passed through unvalidated."""

    @validate_call
    def loose(a: int, *args, **kwargs) -> tuple:
        return a, args, kwargs

    assert loose(1, "x", 2.5, k="v") == (1, ("x", 2.5), {"k": "v"})


def test_validate_call_check_filter_can_select_variadic_parameter() -> None:
    """Verify `check` may name a variadic parameter and restricts validation to it."""

    @validate_call(check=("numbers",))
    def process(label: str, *numbers: int) -> int:
        return sum(numbers)

    assert process(123, 1, 2) == 3  # 'label' is not checked

    with pytest.raises(ValidationError):
        process("ok", 1, "2")


def test_validate_call_var_positional_bypass_switch() -> None:
    """Verify the bypass switch also skips variadic validation."""

    @validate_call
    def total(*numbers: int, _validate_call: bool = True) -> tuple:
        return numbers

    assert total("x", _validate_call=False) == ("x",)

    with pytest.raises(ValidationError):
        total("x")


@pytest.mark.asyncio
async def test_validate_call_async_var_positional() -> None:
    """Verify `*args` validation works on async functions."""

    @validate_call
    async def total(*numbers: int) -> int:
        return sum(numbers)

    assert await total(1, 2) == 3

    with pytest.raises(ValidationError):
        await total(1, "2")


@pytest.mark.asyncio
async def test_validate_call_async_var_keyword() -> None:
    """Verify `**kwargs` validation works on async functions."""

    @validate_call
    async def collect(**options: int) -> dict:
        return options

    assert await collect(a=1) == {"a": 1}

    with pytest.raises(ValidationError):
        await collect(a="1")


# ============================================================================
# Iterable[T] — default behavior (iterators are rejected)
# ============================================================================

def test_validate_call_iterable_rejects_one_shot_iterator_by_default() -> None:
    """Verify a generator passed to Iterable[T] is rejected instead of silently exhausted."""

    @validate_call
    def total(items: Iterable[int]) -> int:
        return sum(items)

    with pytest.raises(ValidationError):
        total(x for x in range(3))


def test_validate_call_iterable_accepts_reiterable_collections_by_default() -> None:
    """Verify list, tuple, set and range pass Iterable[T] unchanged."""

    @validate_call
    def total(items: Iterable[int]) -> int:
        return sum(items)

    assert total([1, 2]) == 3
    assert total((1, 2)) == 3
    assert total({1, 2}) == 3
    assert total(range(3)) == 3


def test_validate_call_bare_iterable_accepts_iterator_by_default() -> None:
    """Verify bare Iterable does no item check, so an iterator stays lazy and intact."""

    @validate_call
    def first(items: Iterable) -> int:
        return next(iter(items))

    iterator = iter([7, 8])
    assert first(iterator) == 7
    assert next(iterator) == 8  # nothing was consumed by validation


# ============================================================================
# materialize_iterators=True
# ============================================================================

def test_validate_call_materialize_iterators_function_receives_tuple() -> None:
    """Verify an iterator is consumed once and the function receives all items as a tuple."""

    @validate_call(materialize_iterators=True)
    def collect(items: Iterable[int]) -> object:
        return items

    assert collect(x for x in range(3)) == (0, 1, 2)
    assert isinstance(collect(iter([1])), tuple)


def test_validate_call_materialize_iterators_result_is_reiterable() -> None:
    """Verify the function can iterate the received value more than once."""

    @validate_call(materialize_iterators=True)
    def twice(items: Iterable[int]) -> int:
        return sum(items) + sum(items)

    assert twice(x for x in range(4)) == 12


def test_validate_call_materialize_iterators_keyword_argument() -> None:
    """Verify conversion works for iterators passed by keyword, including keyword-only."""

    @validate_call(materialize_iterators=True)
    def collect(*, items: Iterable[int]) -> object:
        return items

    assert collect(items=iter([1, 2])) == (1, 2)


def test_validate_call_materialize_iterators_validates_items() -> None:
    """Verify converted items are still validated against T."""

    @validate_call(materialize_iterators=True)
    def total(items: Iterable[int]) -> int:
        return sum(items)

    with pytest.raises(ValidationError):
        total(x for x in [1, "2"])


def test_validate_call_materialize_iterators_keeps_defaults_working() -> None:
    """Verify the final call still gets default values correctly after conversion."""

    @validate_call(materialize_iterators=True)
    def total(items: Iterable[int], bonus: int = 5) -> int:
        return sum(items) + bonus

    assert total(iter([1, 2])) == 8
    assert total(iter([1, 2]), 10) == 13
    assert total(iter([1, 2]), bonus=1) == 4


def test_validate_call_materialize_iterators_optional_annotation() -> None:
    """Verify `Iterable[T] | None` converts an iterator and still accepts None."""

    @validate_call(materialize_iterators=True)
    def collect(items: Iterable[int] | None = None) -> object:
        return items

    assert collect(iter([1, 2])) == (1, 2)
    assert collect(None) is None
    assert collect() is None


def test_validate_call_materialize_iterators_keeps_collections_untouched() -> None:
    """Verify a list passed with the flag on reaches the function as the same list object."""

    @validate_call(materialize_iterators=True)
    def collect(items: Iterable[int]) -> object:
        return items

    data = [1, 2, 3]
    assert collect(data) is data


def test_validate_call_materialize_iterators_leaves_bare_iterable_lazy() -> None:
    """Verify only Iterable[T] parameters are converted; a bare Iterable stays a lazy iterator."""

    @validate_call(materialize_iterators=True)
    def pair(typed: Iterable[int], lazy: Iterable) -> tuple:
        return typed, lazy

    lazy = iter([1, 2])
    typed_result, lazy_result = pair(iter([3]), lazy)

    assert typed_result == (3,)
    assert lazy_result is lazy


def test_validate_call_materialize_iterators_bypass_switch_passes_through() -> None:
    """Verify with `_validate_call=False` nothing is validated and nothing is converted."""

    @validate_call(materialize_iterators=True)
    def collect(items: Iterable[int], *, _validate_call: bool = True) -> object:
        return items

    iterator = iter([1, 2])
    assert collect(iterator, _validate_call=False) is iterator


def test_validate_call_materialize_iterators_with_return_validation() -> None:
    """Verify the flag combines with check_return=True."""

    @validate_call(materialize_iterators=True, check_return=True)
    def total(items: Iterable[int]) -> int:
        return sum(items)

    assert total(x for x in range(4)) == 6


def test_validate_call_materialize_iterators_with_check_filter() -> None:
    """Verify the flag works when `check` still includes the Iterable[T] parameter."""

    @validate_call(materialize_iterators=True, check=("items",))
    def total(items: Iterable[int], other: str) -> int:
        return sum(items)

    assert total(iter([1, 2]), 123) == 3  # 'other' is not checked


@pytest.mark.asyncio
async def test_validate_call_materialize_iterators_async() -> None:
    """Verify conversion also works on async functions."""

    @validate_call(materialize_iterators=True)
    async def collect(items: Iterable[int]) -> object:
        return items

    assert await collect(iter([1, 2])) == (1, 2)

    with pytest.raises(ValidationError):
        await collect(iter(["x"]))


def test_validate_call_materialize_iterators_without_flag_each_call_is_independent() -> None:
    """Verify enabling the flag on one function does not leak to another decorated function."""

    @validate_call(materialize_iterators=True)
    def with_flag(items: Iterable[int]) -> object:
        return items

    @validate_call
    def without_flag(items: Iterable[int]) -> object:
        return items

    assert with_flag(iter([1])) == (1,)

    with pytest.raises(ValidationError):
        without_flag(iter([1]))


# ============================================================================
# materialize_iterators=True — decoration-time guard
# ============================================================================

def test_validate_call_materialize_iterators_without_iterable_parameter_raises() -> None:
    """Verify the flag on a function without any Iterable[T] parameter fails at decoration."""

    with pytest.raises(ParamError) as exc_info:

        @validate_call(materialize_iterators=True)
        def plain(a: int) -> int:
            return a

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_ITERABLE_PARAM_ERROR"


def test_validate_call_materialize_iterators_with_only_bare_iterable_raises() -> None:
    """Verify bare Iterable is not enough for the flag to have an effect."""

    with pytest.raises(ParamError) as exc_info:

        @validate_call(materialize_iterators=True)
        def lazy(items: Iterable) -> None:
            return None

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_ITERABLE_PARAM_ERROR"


def test_validate_call_materialize_iterators_excluded_by_check_raises() -> None:
    """Verify the flag raises when `check` removes the only Iterable[T] parameter."""

    with pytest.raises(ParamError) as exc_info:

        @validate_call(materialize_iterators=True, check=("k",))
        def total(items: Iterable[int], k: int) -> int:
            return k

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_ITERABLE_PARAM_ERROR"


def test_validate_call_materialize_iterators_variadic_iterable_raises() -> None:
    """Verify `*xs: Iterable[int]` is not converted (known limit), so the flag has nothing to do."""

    with pytest.raises(ParamError) as exc_info:

        @validate_call(materialize_iterators=True)
        def gather(*groups: Iterable[int]) -> int:
            return 0

    assert exc_info.value.error_name == "VALIDATE_CALL_NO_ITERABLE_PARAM_ERROR"
