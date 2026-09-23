import pytest

# Tested decorator and exceptions
from simplibs.exception import ParamError, ValidationError
from simplibs.rules import greater_than
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