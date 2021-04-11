"""Set package shortcuts."""

import logging

from pylibjpeg._version import __version__
from pylibjpeg.pydicom.utils import generate_frames  # deprecated
from pylibjpeg.utils import decode


# Setup default logging
_logger = logging.getLogger('pylibjpeg')
_logger.addHandler(logging.NullHandler())
_logger.debug("pylibjpeg v{}".format(__version__))


def debug_logger():
    """Setup the logging for debugging."""
    logger = logging.getLogger('pylibjpeg')
    logger.handlers = []
    handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname).1s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
