"""Tests for standalone decoding."""

import logging

from pylibjpeg import debug_logger


def test_debug_logger():
    """Test __init__.debug_logger()."""
    logger = logging.getLogger("pylibjpeg")
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.NullHandler)

    debug_logger()

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)

    debug_logger()

    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)

    logger.handlers = []
