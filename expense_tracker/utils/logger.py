import logging
import os
from logging.handlers import RotatingFileHandler

"""
This module provides a utility function for setting up logging in the application.

It configures a logger with both file and console handlers, using a rotating file handler
to manage log file sizes.
"""

# Define the default logs directory
DEFAULT_LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')


def setup_logger(name, log_file, level=logging.INFO, logs_dir=DEFAULT_LOGS_DIR):
    """
    Set up a logger with file and console handlers.

    Args:
        name (str): The name of the logger.
        log_file (str): The name of the log file (not full path).
        level (int): The logging level (default: logging.INFO).
        logs_dir (str): The directory for log files (default: DEFAULT_LOGS_DIR).

    Returns:
        logging.Logger: Configured logger object.
    """
    # Constructs the logs directory, if it doesn't already exist
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, log_file)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # File handler for all logs
    file_handler = RotatingFileHandler(log_path, maxBytes=10000000, backupCount=5)
    file_handler.setFormatter(formatter)

    # Console handler for error logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.ERROR)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
