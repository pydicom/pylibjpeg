
import logging
import sys

_logger = logging.getLogger(__name__)

try:
    import data as _data
    globals()['data'] = _data
    # Add to cache - needed for pytest
    sys.modules['pylibjpeg.data'] = _data
    _logger.debug('pylibjpeg-data module loaded')
except ImportError:
    pass
