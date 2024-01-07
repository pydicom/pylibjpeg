import logging
import sys

LOGGER = logging.getLogger(__name__)

try:
    import ljdata as _data

    globals()["data"] = _data
    # Add to cache - needed for pytest
    sys.modules["pylibjpeg.data"] = _data
    LOGGER.debug("pylibjpeg-data module loaded")
except ImportError:
    pass
