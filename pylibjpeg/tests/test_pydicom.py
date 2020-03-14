"""Tests for interacting with pydicom."""

import os
import platform
import sys

import pytest

try:
    import pydicom
    import pydicom.config
    from pylibjpeg.pydicom import pixel_data_handler as handler
    from pylibjpeg.pydicom.utils import generate_frames, reshape_frame
    HAS_PYDICOM = True
except ImportError as exc:
    print(exc)
    HAS_PYDICOM = False

from pylibjpeg.data import get_indexed_datasets
from pylibjpeg.plugins import get_plugins
from pylibjpeg.utils import add_handler, remove_handler

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

    def test_get_pixeldata_no_syntax(self):
        """Test exception raised if syntax not supported."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        ds.file_meta.TransferSyntaxUID = '1.2.3.4'
        msg = (
            r"Unable to convert the pixel data as the transfer syntax is not "
            r"supported by the pylibjpeg pixel data handler"
        )
        with pytest.raises(RuntimeError, match=msg):
            handler.get_pixeldata(ds)

    def test_get_pixeldata_no_lj_syntax(self):
        """Test exception raised if syntax not supported."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        msg = (
            r"The libjpeg plugin is required to decode pixel data with a "
            r"transfer syntax of '1.2.840.10008.1.2.4.50'"
        )
        with pytest.raises(RuntimeError, match=msg):
            handler.get_pixeldata(ds)

    def test_get_pixeldata_no_lj_syntax(self):
        """Test exception raised if syntax not supported."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        ds.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.4.90'
        msg = (
            r"The openjpeg plugin is required to decode pixel data with a "
            r"transfer syntax of '1.2.840.10008.1.2.4.90'"
        )
        with pytest.raises(RuntimeError, match=msg):
            handler.get_pixeldata(ds)


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

    def test_add_remove_handler(self):
        """Test removing the pixel data handler."""
        assert handler in pydicom.config.pixel_data_handlers
        remove_handler()
        assert handler not in pydicom.config.pixel_data_handlers
        add_handler()
        assert handler in pydicom.config.pixel_data_handlers

    def test_should_change_PI(self):
        """Pointless test."""
        result = handler.should_change_PhotometricInterpretation_to_RGB(None)
        assert result is False

    def test_missing_required(self):
        """Test missing required element raises."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        del ds.SamplesPerPixel
        msg = (
            r"Unable to convert the pixel data as the following required "
            r"elements are missing from the dataset: SamplesPerPixel"
        )
        with pytest.raises(AttributeError, match=msg):
            ds.pixel_array

    def test_ybr_full_422(self):
        """Test YBR_FULL_422 data decoded."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['SC_rgb_dcmtk_+eb+cy+np.dcm']['ds']
        assert 'YBR_FULL_422' == ds.PhotometricInterpretation
        arr = ds.pixel_array


@pytest.mark.skipif(not HAS_PYDICOM or not HAS_PLUGINS, reason="No plugins")
class TestUtils(object):
    """Test the pydicom.utils functions."""
    def test_generate_frames_single_1s(self):
        """Test with single frame, 1 sample/px."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 1 == ds.SamplesPerPixel
        frames = generate_frames(ds)
        arr = next(frames)
        with pytest.raises(StopIteration):
            next(frames)

        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape
        assert 64 == arr[76, 22]

    def test_generate_frames_1s(self):
        """Test with multiple frames, 1 sample/px."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.80')
        ds = index['emri_small_jpeg_ls_lossless.dcm']['ds']
        assert ds.NumberOfFrames > 1
        assert 1 == ds.SamplesPerPixel
        frames = generate_frames(ds)
        arr = next(frames)

        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape
        assert 163 == arr[12, 23]

    def test_generate_frames_3s_0p(self):
        """Test with multiple frames, 3 sample/px, 0 planar conf."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['color3d_jpeg_baseline.dcm']['ds']
        assert ds.NumberOfFrames > 1
        assert 3 == ds.SamplesPerPixel
        assert 0 == ds.PlanarConfiguration
        frames = generate_frames(ds)
        arr = next(frames)

        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns, 3) == arr.shape
        assert [48,  128,  128] == arr[159, 290, :].tolist()

    @pytest.mark.skip()
    def test_generate_frames_3s_1p(self):
        """Test 3 sample/px, 1 planar conf."""
        # No data
        pass
