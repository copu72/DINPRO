import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler


class Logger:
    _instance = None

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(
        self,
        level: str = "INFO",
        file_path: str | Path | None = None,
        max_bytes: int = 5_242_880,
        backup_count: int = 3,
    ) -> None:
        if self._initialized:
            return

        self._logger = logging.getLogger("dinpro")
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self._logger.handlers.clear()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        self._file_path = None
        if file_path:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                path, maxBytes=max_bytes, backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
            self._file_path = str(path)

        self._initialized = True
        self._level = level.upper()

    def debug(self, message: str, module: str | None = None) -> None:
        self._log(logging.DEBUG, message, module)

    def info(self, message: str, module: str | None = None) -> None:
        self._log(logging.INFO, message, module)

    def warning(self, message: str, module: str | None = None) -> None:
        self._log(logging.WARNING, message, module)

    def error(self, message: str, module: str | None = None) -> None:
        self._log(logging.ERROR, message, module)

    def critical(self, message: str, module: str | None = None) -> None:
        self._log(logging.CRITICAL, message, module)

    def exception(self, message: str, module: str | None = None) -> None:
        self._logger.exception(f"[{module or 'core'}] {message}")

    def set_level(self, level: str) -> None:
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self._level = level.upper()

    def _log(self, level: int, message: str, module: str | None) -> None:
        prefix = f"[{module}] " if module else ""
        self._logger.log(level, f"{prefix}{message}")

    @property
    def level(self) -> str:
        return self._level

    @property
    def file_path(self) -> str | None:
        return getattr(self, "_file_path", None)
