import logging
import logging.handlers

from core.config import BASE_DIR


def setup_logging():
    """
    Set up centralized logging configuration.

    Creates a logger that writes all logs to a single file with rotation.
    Also configures console logging for development.
    """
    # Create logs directory if it doesn't exist
    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Main log file path
    log_file = logs_dir / "app.log"

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s - %(name)s - %(message)s"
    )

    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Suppress some noisy loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return root_logger


# Global logger instance
logger = setup_logging()
