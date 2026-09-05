import logging
from unittest.mock import MagicMock
from simplibs.validate.tools.log_this._helpers import log_start


def test_log_start_emits_expected_log() -> None:
    """Verify log_start calls logger.log with correct level and formatted message."""
    mock_logger = MagicMock(spec=logging.Logger)

    log_start(
        logger=mock_logger,
        level=logging.INFO,
        func_name="process_data",
        call_repr="a=10, b='test'",
    )

    mock_logger.log.assert_called_once_with(
        logging.INFO,
        "Calling %s(%s)",
        "process_data",
        "a=10, b='test'",
    )