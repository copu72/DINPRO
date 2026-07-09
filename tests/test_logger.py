import io
import logging
import sys
from pathlib import Path

from dinpro.core.logger import Logger


class TestLogger:
    def setup_method(self):
        Logger._instance = None

    def test_singleton(self):
        logger1 = Logger()
        logger2 = Logger()
        assert logger1 is logger2

    def test_initialize_and_log(self):
        logger = Logger()
        logger.initialize(level="DEBUG")

        captured = io.StringIO()
        handler = logging.StreamHandler(captured)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger._logger.handlers.clear()
        logger._logger.addHandler(handler)

        logger.info("Test message", "test")
        output = captured.getvalue()
        assert "Test message" in output
        assert "[test]" in output

    def test_levels(self):
        logger = Logger()
        logger.initialize(level="WARNING")
        assert logger.level == "WARNING"
        logger.set_level("DEBUG")
        assert logger.level == "DEBUG"

    def test_file_logging(self, tmp_path: Path):
        logger = Logger()
        log_file = tmp_path / "test.log"
        logger.initialize(level="INFO", file_path=str(log_file))
        logger.info("File test")
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "File test" in content

    def test_no_cross_contamination(self):
        Logger._instance = None
        logger = Logger()
        logger.initialize(level="INFO")
        logger.info("Should work")
