import logging
import os

from llm4netlab.config import BASE_DIR


class SystemLogger:
    def __init__(self):
        log_path = os.path.join(BASE_DIR, "runtime", "system.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        self.log_path = log_path

        self.logger = logging.getLogger("SystemLogger")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if not self.logger.handlers:
            self._create_handler()
            return

        if not os.path.exists(self.log_path):
            self._recreate_handler()

    def _create_handler(self):
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8", mode="a")
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _recreate_handler(self):
        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)
        self._create_handler()


system_logger = SystemLogger().logger


def refresh_logger():
    """Refresh the logger by re-initializing it."""
    global system_logger
    system_logger = SystemLogger().logger
    return system_logger
