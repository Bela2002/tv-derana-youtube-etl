import logging
from pathlib import Path


def setup_logger() -> logging.Logger:
    """
    Configure application logging.

    Logs are written both to the console and to logs/etl.log.
    """

    log_directory = Path("logs")
    log_directory.mkdir(exist_ok=True)

    logger = logging.getLogger("tv_derana_etl")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logger() is called again.
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_directory / "etl.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger