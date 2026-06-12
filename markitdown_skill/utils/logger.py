import logging
import sys

def setup_logger(name: str = "markitdown_skill", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with the given name and level.
    """
    logger = logging.getLogger(name)
    # Avoid duplicate handlers if logger is initialized multiple times
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        formatter = logging.Formatter('[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # Prevent logging from propagating to root logger to avoid double print
        logger.propagate = False
    return logger
