"""Set package shortcuts."""

import logging
import sys


from ._version import __version__
from .utils import decode, add_handler


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


try:
    import pydicom
    _logger.debug('pydicom module loaded')
    from pylibjpeg.pydicom.utils import generate_frames

    # We only add a handler if pydicom doesn't already have one
    try:
        import pydicom.pixel_data_handlers.pylibjpeg_handler
    except ImportError:
        add_handler()

except ImportError:
    pass
