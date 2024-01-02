"""Set package shortcuts."""

import logging

from pylibjpeg._version import __version__
from pylibjpeg.utils import decode  # noqa: F401


# Setup default logging
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_logger.debug(f"pylibjpeg v{__version__}")


def debug_logger() -> None:
    """Setup the logging for debugging."""
    logger = logging.getLogger(__name__)
    logger.handlers = []
    handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname).1s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
