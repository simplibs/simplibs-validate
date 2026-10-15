import logging
from unittest.mock import MagicMock
import pytest

from simplibs.exception import ParamError
from simplibs.validate.decorators.log_this import log_this


class _CountingRepr:
    """Counts how many times its repr is actually built."""

    def __init__(self) -> None:
        self.calls = 0

    def __repr__(self) -> str:
        self.calls += 1
        return "counted"


def _silent_logger(enabled: set[int] | None = None) -> MagicMock:
    """A mock logger whose isEnabledFor() answers True only for the given levels."""
    mock_logger = MagicMock(spec=logging.Logger)
    mock_logger.isEnabledFor.side_effect = lambda lvl: lvl in (enabled or set())
    return mock_logger


# ============================================================================
# Synchronous Functions Testing
# ============================================================================

def test_log_this_bare_sync_success() -> None:
    """Verify bare @log_this logs start and success at DEBUG level by default."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(logger=mock_logger)
    def add(a: int, b: int) -> int:
        return a + b

    result = add(2, 3)
    assert result == 5

    # Should call log twice: start and success
    assert mock_logger.log.call_count == 2

    # Verify log_start
    start_call = mock_logger.log.call_args_list[0]
    assert start_call.args[0] == logging.DEBUG
    assert start_call.args[1] == "Calling %s(%s)"

    # Verify log_success (the result is logged as already-rendered text)
    success_call = mock_logger.log.call_args_list[1]
    assert success_call.args[0] == logging.DEBUG
    assert success_call.args[1] == "%s(%s) returned %s in %.4fs"
    assert success_call.args[4] == "5"


def test_log_this_custom_level_and_masking() -> None:
    """Verify level override and excluded parameter masking."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(
        level=logging.INFO,
        exclude=("password",),
        logger=mock_logger,
    )
    def login(user: str, password: str) -> bool:
        return True

    assert login("alice", "secret123") is True

    start_call = mock_logger.log.call_args_list[0]
    assert start_call.args[0] == logging.INFO
    assert "password=***" in start_call.args[3]
    assert "secret123" not in start_call.args[3]


def test_log_this_log_result_disabled() -> None:
    """Verify return value is omitted when log_result is False."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(log_result=False, logger=mock_logger)
    def get_token() -> str:
        return "sensitive_token"

    assert get_token() == "sensitive_token"

    success_call = mock_logger.log.call_args_list[1]
    assert success_call.args[1] == "%s(%s) completed in %.4fs"
    assert "sensitive_token" not in success_call.args


def test_log_this_exception_handling() -> None:
    """Verify exceptions are logged with exc_info=True and re-raised unchanged."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(logger=mock_logger)
    def fail() -> None:
        raise ValueError("Database connection failed")

    with pytest.raises(ValueError, match="Database connection failed"):
        fail()

    mock_logger.error.assert_called_once()
    _, kwargs = mock_logger.error.call_args
    assert kwargs.get("exc_info") is True


def test_log_this_disable_exception_logging() -> None:
    """Verify exception logging can be disabled with log_exceptions=False."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(log_exceptions=False, logger=mock_logger)
    def silent_fail() -> None:
        raise RuntimeError("Silent failure")

    with pytest.raises(RuntimeError):
        silent_fail()

    mock_logger.error.assert_not_called()


# ============================================================================
# Asynchronous Functions Testing
# ============================================================================

async def test_log_this_async_success() -> None:
    """Verify @log_this logs start and completion for async functions."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(logger=mock_logger)
    async def async_compute(x: int) -> int:
        return x * 2

    result = await async_compute(10)
    assert result == 20

    assert mock_logger.log.call_count == 2
    success_call = mock_logger.log.call_args_list[1]
    assert success_call.args[4] == "20"


async def test_log_this_async_exception_handling() -> None:
    """Verify async exceptions are logged and re-raised."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(logger=mock_logger)
    async def async_fail() -> None:
        raise KeyError("Missing key")

    with pytest.raises(KeyError):
        await async_fail()

    mock_logger.error.assert_called_once()
    _, kwargs = mock_logger.error.call_args
    assert kwargs.get("exc_info") is True


def test_log_this_prevents_double_wrapping() -> None:
    """Verify that decorating a function multiple times with @log_this unwraps previous layers and prevents duplicate logs."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(logger=mock_logger)
    @log_this(logger=mock_logger)
    def multiply(a: int, b: int) -> int:
        return a * b

    assert multiply(3, 4) == 12

    # Pouze 2 zprávy (1x start, 1x success) namísto 4 zdvojených zpráv
    assert mock_logger.log.call_count == 2
    assert getattr(multiply, "_is_log_this_wrapper", False) is True


def test_log_this_includes_applied_default_arguments() -> None:
    """Verify bound.apply_defaults() ensures default parameter values are formatted in call signature."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(logger=mock_logger)
    def fetch_page(url: str, timeout: int = 30) -> str:
        return "data"

    fetch_page("https://example.com")

    # Ověříme, že v logovaném signature je obsažen i defaultní argument timeout=30
    start_call = mock_logger.log.call_args_list[0]
    call_repr = start_call.args[3]
    assert "timeout=30" in call_repr


# ============================================================================
# Shortening of large values (max_items)
# ============================================================================

def test_log_this_shortens_large_result_by_default() -> None:
    """Verify a large result is shortened without any configuration."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(logger=mock_logger)
    def collect() -> list[int]:
        return list(range(1000))

    assert collect() == list(range(1000))  # the real return value is never touched

    success_call = mock_logger.log.call_args_list[1]
    assert success_call.args[4] == "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...] (1000 items)"


def test_log_this_shortens_large_argument_by_default() -> None:
    """Verify a large argument is shortened in the entry record as well."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(logger=mock_logger)
    def count(paths: list[int]) -> int:
        return len(paths)

    assert count(list(range(1000))) == 1000

    start_call = mock_logger.log.call_args_list[0]
    assert "(1000 items)" in start_call.args[3]
    assert len(start_call.args[3]) < 200


def test_log_this_custom_max_items() -> None:
    """Verify max_items changes the number of shown items."""
    mock_logger = MagicMock(spec=logging.Logger)

    @log_this(max_items=2, logger=mock_logger)
    def collect() -> list[int]:
        return [1, 2, 3, 4]

    collect()

    assert mock_logger.log.call_args_list[1].args[4] == "[1, 2, ...] (4 items)"


def test_log_this_max_items_none_logs_everything() -> None:
    """Verify max_items=None restores the full repr."""
    mock_logger = MagicMock(spec=logging.Logger)
    data = list(range(50))

    @log_this(max_items=None, logger=mock_logger)
    def collect() -> list[int]:
        return data

    collect()

    assert mock_logger.log.call_args_list[1].args[4] == repr(data)


@pytest.mark.parametrize("invalid", [0, -5, True, "10"])
def test_log_this_invalid_max_items_raises_at_decoration_time(invalid: object) -> None:
    """Verify a wrong max_items fails when the decorator is applied, not on first call."""
    with pytest.raises(ParamError):
        @log_this(max_items=invalid)  # type: ignore[arg-type]
        def func() -> None: ...


def test_log_this_broken_repr_does_not_break_the_call() -> None:
    """Verify an argument with a failing __repr__ never breaks the decorated function."""
    mock_logger = MagicMock(spec=logging.Logger)

    class Broken:
        def __repr__(self) -> str:
            raise RuntimeError("broken repr")

    @log_this(logger=mock_logger)
    def passthrough(value: Broken) -> Broken:
        return value

    obj = Broken()
    assert passthrough(obj) is obj
    assert mock_logger.log.call_count == 2


# ============================================================================
# Nothing is formatted when nothing would be logged
# ============================================================================

def test_log_this_fast_path_when_nothing_enabled() -> None:
    """Verify a fully disabled logger means a direct call and no formatting."""
    mock_logger = _silent_logger(enabled=set())
    spy = _CountingRepr()

    @log_this(logger=mock_logger)
    def echo(value: object) -> object:
        return value

    assert echo(spy) is spy

    assert spy.calls == 0
    mock_logger.log.assert_not_called()
    mock_logger.error.assert_not_called()


def test_log_this_success_formats_nothing_when_only_error_enabled() -> None:
    """Verify the usual production state (DEBUG off, ERROR on) formats nothing for a successful call."""
    mock_logger = _silent_logger(enabled={logging.ERROR})
    spy = _CountingRepr()

    @log_this(logger=mock_logger)
    def echo(value: object) -> object:
        return value

    assert echo(spy) is spy

    assert spy.calls == 0
    mock_logger.log.assert_not_called()
    mock_logger.error.assert_not_called()


def test_log_this_failure_formats_arguments_lazily_when_only_error_enabled() -> None:
    """Verify the call signature is built only when the call raises."""
    mock_logger = _silent_logger(enabled={logging.ERROR})
    spy = _CountingRepr()

    @log_this(logger=mock_logger)
    def fail(value: object) -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        fail(spy)

    mock_logger.log.assert_not_called()
    mock_logger.error.assert_called_once()
    assert "value=counted" in mock_logger.error.call_args.args[2]
    assert spy.calls == 1


def test_log_this_failure_with_unrenderable_arguments_keeps_original_exception() -> None:
    """Verify a wrong call still raises the original TypeError, with a placeholder in the log."""
    mock_logger = _silent_logger(enabled={logging.ERROR})

    @log_this(logger=mock_logger)
    def one_arg(a: int) -> int:
        return a

    with pytest.raises(TypeError) as excinfo:
        one_arg(1, 2, 3)  # type: ignore[call-arg]

    assert excinfo.value.__context__ is None
    assert mock_logger.error.call_args.args[2] == "<arguments unavailable>"


def test_log_this_failure_describes_arguments_as_at_entry_when_entry_level_enabled() -> None:
    """Verify that with the entry level enabled the signature is captured before the call."""
    mock_logger = _silent_logger(enabled={logging.DEBUG, logging.ERROR})

    @log_this(logger=mock_logger)
    def fail(items: list[int]) -> None:
        items.append(99)
        raise ValueError("boom")

    with pytest.raises(ValueError):
        fail([1])

    assert mock_logger.error.call_args.args[2] == "items=[1]"


def test_log_this_lazy_failure_describes_arguments_as_at_failure() -> None:
    """Verify the documented trade-off: a lazily built failure signature shows in-place mutations."""
    mock_logger = _silent_logger(enabled={logging.ERROR})

    @log_this(logger=mock_logger)
    def fail(items: list[int]) -> None:
        items.append(99)
        raise ValueError("boom")

    with pytest.raises(ValueError):
        fail([1])

    assert mock_logger.error.call_args.args[2] == "items=[1, 99]"


def test_log_this_masked_argument_is_never_rendered() -> None:
    """Verify an excluded argument is not even repr'd."""
    mock_logger = MagicMock(spec=logging.Logger)
    secret = _CountingRepr()

    @log_this(exclude=("token",), logger=mock_logger)
    def use(token: object) -> None: ...

    use(secret)

    assert secret.calls == 0


async def test_log_this_async_fast_path() -> None:
    """Verify the async wrapper also skips all formatting when nothing is enabled."""
    mock_logger = _silent_logger(enabled=set())
    spy = _CountingRepr()

    @log_this(logger=mock_logger)
    async def echo(value: object) -> object:
        return value

    assert await echo(spy) is spy

    assert spy.calls == 0
    mock_logger.log.assert_not_called()


async def test_log_this_async_failure_formats_arguments_lazily() -> None:
    """Verify the async wrapper builds the failure signature only when the call raises."""
    mock_logger = _silent_logger(enabled={logging.ERROR})
    spy = _CountingRepr()

    @log_this(logger=mock_logger)
    async def fail(value: object) -> None:
        raise KeyError("missing")

    with pytest.raises(KeyError):
        await fail(spy)

    mock_logger.log.assert_not_called()
    assert "value=counted" in mock_logger.error.call_args.args[2]


# ============================================================================
# Integration with a real logger
# ============================================================================

def test_log_this_real_logger_debug_enabled(caplog: pytest.LogCaptureFixture) -> None:
    """Verify end-to-end output through the function's own module logger."""
    @log_this
    def collect(root: str) -> list[int]:
        return list(range(1000))

    with caplog.at_level(logging.DEBUG, logger=__name__):
        collect("/project")

    assert "Calling" in caplog.text
    assert "collect(root='/project')" in caplog.text
    assert "(1000 items)" in caplog.text


def test_log_this_real_logger_info_level_logs_nothing(caplog: pytest.LogCaptureFixture) -> None:
    """Verify nothing is emitted (or formatted) at INFO with the default DEBUG level."""
    spy = _CountingRepr()

    @log_this
    def echo(value: object) -> object:
        return value

    with caplog.at_level(logging.INFO, logger=__name__):
        echo(spy)

    assert caplog.records == []
    assert spy.calls == 0
