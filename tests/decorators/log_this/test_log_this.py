import logging
from unittest.mock import MagicMock
import pytest

from simplibs.validate.decorators.log_this import log_this


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

    # Verify log_success
    success_call = mock_logger.log.call_args_list[1]
    assert success_call.args[0] == logging.DEBUG
    assert success_call.args[1] == "%s(%s) returned %r in %.4fs"
    assert success_call.args[4] == 5


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
    assert success_call.args[4] == 20


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