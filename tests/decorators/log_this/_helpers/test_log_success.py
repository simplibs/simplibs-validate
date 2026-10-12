import logging
from unittest.mock import MagicMock
from simplibs.validate.decorators.log_this._helpers import build_repr_func, log_success


def test_log_success_logs_result_through_repr_func() -> None:
    """Verify the result is rendered by repr_func and logged as text."""
    mock_logger = MagicMock(spec=logging.Logger)

    log_success(
        mock_logger, logging.INFO, "load", "a=1", 0.0, [1, 2, 3], True,
        repr_func=lambda value: "RENDERED",
    )

    args = mock_logger.log.call_args.args
    assert args[0] == logging.INFO
    assert args[1] == "%s(%s) returned %s in %.4fs"
    assert args[2:5] == ("load", "a=1", "RENDERED")


def test_log_success_default_repr_func_is_plain_repr() -> None:
    """Verify calling log_success without repr_func keeps the plain repr behavior."""
    mock_logger = MagicMock(spec=logging.Logger)

    log_success(mock_logger, logging.DEBUG, "load", "a=1", 0.0, [1, 2], True)

    assert mock_logger.log.call_args.args[4] == "[1, 2]"


def test_log_success_bounded_result() -> None:
    """Verify a huge result is shortened when a bounded repr_func is given."""
    mock_logger = MagicMock(spec=logging.Logger)

    log_success(
        mock_logger, logging.DEBUG, "load", "a=1", 0.0, list(range(1000)), True,
        repr_func=build_repr_func(2),
    )

    assert mock_logger.log.call_args.args[4] == "[0, 1, ...] (1000 items)"


def test_log_success_without_result_never_renders_it() -> None:
    """Verify log_result=False omits the result and does not render it at all."""
    mock_logger = MagicMock(spec=logging.Logger)
    rendered: list[object] = []

    log_success(
        mock_logger, logging.DEBUG, "load", "a=1", 0.0, "secret", False,
        repr_func=lambda value: rendered.append(value) or "x",
    )

    args = mock_logger.log.call_args.args
    assert args[1] == "%s(%s) completed in %.4fs"
    assert "secret" not in args
    assert rendered == []


def test_log_success_falsy_result_is_logged_like_any_other() -> None:
    """Verify False/None/0 are not treated as failure."""
    for falsy in (False, None, 0, []):
        mock_logger = MagicMock(spec=logging.Logger)
        log_success(mock_logger, logging.DEBUG, "f", "", 0.0, falsy, True)
        assert mock_logger.log.call_args.args[4] == repr(falsy)
