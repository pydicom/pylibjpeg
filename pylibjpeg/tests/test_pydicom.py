"""Tests for interacting with pydicom."""

import os
import platform
import sys

import pytest

try:
    import pydicom
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False

from pylibjpeg import _plugin_manager

HAS_PLUGINS = False
if _plugin_manager.plugins:
    HAS_PLUGINS = True


@pytest.mark.skipif(not HAS_PYDICOM or HAS_PLUGINS)
class TestNoPlugins(object):
    """Test interactions with no plugins."""
    # Should basically just not mess up the usual pydicom behaviour
    pass


@pytest.mark.skipif(not HAS_PYDICOM or not HAS_PLUGINS)
class TestPlugins(object):
    """Test interaction with plugins."""
    # Simple tests to ensure plugins work as intended
    pass


# May need pydicom to reload some data if dynamically changing
#   available plugins
