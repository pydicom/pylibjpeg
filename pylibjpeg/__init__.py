"""Set package shortcuts."""

import logging
import sys


from ._version import __version__
from ._config import PLUGINS
from .plugins import load_plugins


# Setup default logging
LOGGER = logging.getLogger('pynetdicom')
LOGGER.addHandler(logging.NullHandler())
LOGGER.debug("pylibjpeg v{}".format(__version__))


def debug_logger():
    """Setup the logging for debugging."""
    logger = logging.getLogger('pylibjpeg')
    logger.handlers = []
    handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname).1s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# TODO: remove this later
debug_logger()


try:
    import data as _data
    globals()['data'] = _data
    # Add to cache - needed for pytest
    sys.modules['pylibjpeg.data'] = _data
    LOGGER.debug('pylibjpeg-data module loaded')
except ImportError:
    pass

load_plugins(PLUGINS)

from .utils import add_handler

try:
    import pydicom
    add_handler()
    LOGGER.debug('pydicom module loaded')
except ImportError:
    pass
