import sys
from logging import (
    DEBUG,
    ERROR,
    WARNING,
    getLogger,
    Formatter,
    StreamHandler,
)

FORMATTER = Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s'
)


def init_logging():
    root = getLogger()
    root.setLevel(DEBUG)
    root.addHandler(err_handler())
    root.addHandler(warning_handler())
    return root


def err_handler():
    handler = StreamHandler(sys.stdout)
    handler.setFormatter(FORMATTER)
    handler.setLevel(ERROR)
    return handler


def warning_handler():
    handler = StreamHandler(sys.stdout)
    handler.setFormatter(FORMATTER)
    handler.setLevel(WARNING)
    return handler
