import logging
from pathlib import Path


def get_logger(name=None, level=logging.INFO, logfile_name='portfolio.log'):
    """Return a configured logger. Ensures a `logs/` directory exists and
    attaches both a console and a file handler (append mode).

    Args:
        name: logger name (None for root-like behaviour)
        level: logging level
        logfile_name: filename used inside `logs/` folder
    """
    root = logging.getLogger()
    logs_dir = Path(__file__).parent / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    logfile = logs_dir / logfile_name

    if not root.handlers:
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        root.addHandler(ch)

        # File handler
        fh = logging.FileHandler(filename=str(logfile), mode='a', encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        root.addHandler(fh)

        root.setLevel(level)

    return logging.getLogger(name)


# module-level logger convenience instance
logger = get_logger(__name__)

__all__ = ["get_logger", "logger"]
