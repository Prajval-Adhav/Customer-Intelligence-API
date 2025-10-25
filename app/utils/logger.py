import logging
import os
from datetime import datetime

def get_logger(name: str = "app", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.handlers:
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        # Create log file with date in name
        log_filename = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y-%m-%d')}.log")

        # Console handler
        stream_handler = logging.StreamHandler()
        # File handler
        file_handler = logging.FileHandler(log_filename, mode='a')

        # Formatter
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

        logger.propagate = False

    return logger
