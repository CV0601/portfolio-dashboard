import logging

def get_logger(name=None, level=logging.INFO):
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    return logging.getLogger(name)

# module-level logger convenience instance
logger = get_logger(__name__)

__all__ = ["get_logger", "logger"]
