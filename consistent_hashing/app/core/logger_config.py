import logging
from logging.handlers import TimedRotatingFileHandler
import sys

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def setup_logger(name: str, level=logging.INFO, log_file: str = None) -> logging.Logger:
    """
    This function configures a logger to output messages to the console and,
    optionally, to a time-rotating file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(LOG_FORMAT)

    if logger.hasHandlers():
        logger.handlers.clear()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file:
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',  # Rotate logs daily
            backupCount=7,    # Keep 7 days of logs
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False

    return logger

