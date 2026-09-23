import logging
import time
from unittest.mock import MagicMock
from simplibs.validate.decorators.log_this._helpers import log_success


def test_log_success_with_result_enabled() -> None:
    """Verify log_success includes return value and elapsed time when log_result is True."""
    mock_logger = MagicMock(spec=logging.Logger)
    started = time.perf_counter() - 0.5  # Simulate 0.5s runtime

    log_success(
        logger=mock_logger,
        level=logging.INFO,
        func_name="calculate",
        call_repr="x=5",
        started=started,
        result=42,
        log_result=True,
    )

    mock_logger.log.assert_called_once()
    args, _ = mock_logger.log.call_args
    assert args[0] == logging.INFO
    assert args[1] == "%s(%s) returned %r in %.4fs"
    assert args[2] == "calculate"
    assert args[3] == "x=5"
    assert args[4] == 42


def test_log_success_with_result_disabled() -> None:
    """Verify log_success omits return value when log_result is False."""
    mock_logger = MagicMock(spec=logging.Logger)
    started = time.perf_counter() - 0.1

    log_success(
        logger=mock_logger,
        level=logging.DEBUG,
        func_name="fetch_secret",
        call_repr="id=1",
        started=started,
        result="super_secret_token",
        log_result=False,
    )

    mock_logger.log.assert_called_once()
    args, _ = mock_logger.log.call_args
    assert args[0] == logging.DEBUG
    assert args[1] == "%s(%s) completed in %.4fs"
    assert "super_secret_token" not in args


def test_log_success_falsy_result() -> None:
    """Verify falsy return values (e.g. False, None, 0) are logged normally as valid results."""
    mock_logger = MagicMock(spec=logging.Logger)
    started = time.perf_counter()

    log_success(
        logger=mock_logger,
        level=logging.INFO,
        func_name="is_valid",
        call_repr="val=-1",
        started=started,
        result=False,
        log_result=True,
    )

    args, _ = mock_logger.log.call_args
    assert args[4] is False