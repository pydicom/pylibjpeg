"""Set package shortcuts."""

import sys

from ._version import __version__
from .libjpeg import decode, add_handler, remove_handler, get_parameters


# Add the testing data to pylibjpeg (if available)
try:
    import data as _data
    globals()['data'] = _data
    # Add to cache - needed for pytest
    sys.modules['pylibjpeg.data'] = _data
except ImportError:
    pass

# Add the pixel data handler to pydicom (if available)
try:
    import pydicom
    add_handler()
except ImportError:
    pass
