"""Set package shortcuts."""

from ._version import __version__
from .libjpeg import decode, add_handler, remove_handler, get_parameters

try:
    import pydicom
    add_handler()
except ImportError:
    pass
