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

from pylibjpeg.plugins import get_plugins
from pylibjpeg.data import get_indexed_datasets

HAS_PLUGINS = get_plugins() != []


@pytest.mark.skipif(not HAS_PYDICOM or HAS_PLUGINS, reason="Plugins available")
class TestNoPlugins(object):
    """Test interactions with no plugins."""
    def test_pixel_array(self):
        # Should basically just not mess up the usual pydicom behaviour
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        msg = (
            r"The following handlers are available to decode the pixel data "
            r"however they are missing required dependencies: GDCM \(req. "
            r"GDCM\), Pillow \(req. Pillow\), pylibjpeg \(req. libjpeg "
            r"plugin, openjpeg plugin\)"
        )
        with pytest.raises(RuntimeError, match=msg):
            ds.pixel_array


@pytest.mark.skipif(not HAS_PYDICOM or not HAS_PLUGINS, reason="No plugins")
class TestPlugins(object):
    """Test interaction with plugins."""
    def test_pixel_array(self):
        # Should basically just not mess up the usual pydicom behaviour
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        arr = ds.pixel_array

        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        # Reference values from GDCM handler
        assert  76 == arr[ 5, 50]
        assert 167 == arr[15, 50]
        assert 149 == arr[25, 50]
        assert 203 == arr[35, 50]
        assert  29 == arr[45, 50]
        assert 142 == arr[55, 50]
        assert   1 == arr[65, 50]
        assert  64 == arr[75, 50]
        assert 192 == arr[85, 50]
        assert 255 == arr[95, 50]
