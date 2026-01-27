import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

def setup_logger(level: str = 'INFO', log_dir: str = 'logs'):
    """Configure application logging with rotation"""

    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    rotate_file = RotatingFileHandler(
        log_path / 'backup_utility.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    rotate_file.setLevel(logging.DEBUG)
    rotate_file.setFormatter(formatter)
    logger.addHandler(rotate_file)

    error_logs = RotatingFileHandler(
        log_path / 'errors.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    error_logs.setLevel(logging.ERROR)
    error_logs.setFormatter(formatter)
    logger.addHandler(error_logs)

    return logger
