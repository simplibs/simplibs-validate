import logging
import time
from unittest.mock import MagicMock
import pytest
from simplibs.validate.decorators.log_this._helpers import log_exception


def test_log_exception_enabled() -> None:
    """Verify log_exception emits logger.error with exc_info=True inside exception context."""
    mock_logger = MagicMock(spec=logging.Logger)
    started = time.perf_counter() - 0.2

    try:
        raise ValueError("Something went wrong")
    except ValueError:
        log_exception(
            logger=mock_logger,
            log_exceptions=True,
            func_name="failing_func",
            call_repr="x=0",
            started=started,
        )

    mock_logger.error.assert_called_once()
    args, kwargs = mock_logger.error.call_args
    assert args[0] == "%s(%s) raised after %.4fs"
    assert args[1] == "failing_func"
    assert args[2] == "x=0"
    assert kwargs.get("exc_info") is True


def test_log_exception_disabled() -> None:
    """Verify log_exception does nothing when log_exceptions is False."""
    mock_logger = MagicMock(spec=logging.Logger)
    started = time.perf_counter()

    try:
        raise RuntimeError("Ignored failure")
    except RuntimeError:
        log_exception(
            logger=mock_logger,
            log_exceptions=False,
            func_name="silent_fail",
            call_repr="",
            started=started,
        )

    mock_logger.error.assert_not_called()