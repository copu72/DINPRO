import logging
from pathlib import Path

from dinpro.core.logger import Logger


class TestLoggerEdge:
    def setup_method(self):
        Logger._instance = None

    def test_all_levels(self):
        logger = Logger()
        logger.initialize(level="DEBUG")
        logger.debug("debug msg", "test")
        logger.info("info msg", "test")
        logger.warning("warn msg", "test")
        logger.error("error msg", "test")
        logger.critical("critical msg", "test")

    def test_exception_logging(self):
        logger = Logger()
        logger.initialize(level="DEBUG")
        try:
            raise ValueError("test error")
        except ValueError:
            logger.exception("Caught error", "test")

    def test_set_level_runtime(self):
        logger = Logger()
        logger.initialize(level="INFO")
        assert logger.level == "INFO"
        logger.set_level("DEBUG")
        assert logger.level == "DEBUG"

    def test_second_initialize_noop(self):
        logger = Logger()
        logger.initialize(level="INFO")
        logger.initialize(level="DEBUG")
        assert logger.level == "INFO"

    def test_log_without_module(self):
        logger = Logger()
        logger.initialize()
        logger.info("no module")

    def test_file_path_property(self):
        logger = Logger()
        assert logger.file_path is None
        logger.initialize(file_path="test.log")
        logger.info("test")
