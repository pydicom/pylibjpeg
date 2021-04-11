"""Tests for interacting with pydicom."""

import os
import platform
import sys

import pytest

try:
    import pydicom
    import pydicom.config
    HAS_PYDICOM = True
except ImportError as exc:
    HAS_PYDICOM = False

from pylibjpeg.data import get_indexed_datasets
from pylibjpeg.pydicom.utils import get_j2k_parameters, generate_frames
from pylibjpeg.utils import get_pixel_data_decoders


decoders = get_pixel_data_decoders()
HAS_PLUGINS = bool(decoders)
HAS_JPEG_PLUGIN = '1.2.840.10008.1.2.4.50' in decoders
HAS_JPEG_LS_PLUGIN = '1.2.840.10008.1.2.4.80' in decoders
HAS_JPEG_2K_PLUGIN = '1.2.840.10008.1.2.4.90' in decoders

RUN_JPEG = HAS_JPEG_PLUGIN and HAS_PYDICOM
RUN_JPEGLS = HAS_JPEG_LS_PLUGIN and HAS_PYDICOM
RUN_JPEG2K = HAS_JPEG_2K_PLUGIN and HAS_PYDICOM

PY_VERSION = sys.version[:2]


@pytest.mark.skipif(not HAS_PYDICOM or HAS_PLUGINS, reason="Plugins available")
class TestNoPlugins:
    """Test interactions with no plugins."""
    def test_pixel_array(self):
        # Should basically just not mess up the usual pydicom behaviour
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        msg = (
            r"Unable to convert the Pixel Data as the 'pylibjpeg-libjpeg' "
            r"plugin is not installed"
        )
        with pytest.raises(RuntimeError, match=msg):
            ds.pixel_array


@pytest.mark.skipif(not HAS_PYDICOM, reason="No pydicom")
class TestPlugins:
    """Test interaction with plugins."""
    @pytest.mark.skipif(not RUN_JPEG, reason="No JPEG plugin")
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

    @pytest.mark.skipif(not RUN_JPEG, reason="No JPEG plugin")
    def test_missing_required(self):
        """Test missing required element raises."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        del ds.SamplesPerPixel

        msg = r"'FileDataset' object has no attribute 'SamplesPerPixel'"
        with pytest.raises(AttributeError, match=msg):
            ds.pixel_array

    @pytest.mark.skipif(not RUN_JPEG, reason="No JPEG plugin")
    def test_ybr_full_422(self):
        """Test YBR_FULL_422 data decoded."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index['SC_rgb_dcmtk_+eb+cy+np.dcm']['ds']
        assert 'YBR_FULL_422' == ds.PhotometricInterpretation
        arr = ds.pixel_array


@pytest.mark.skipif(not RUN_JPEG, reason="No JPEG plugin")
class TestJPEGPlugin:
    """Test interaction with plugins that support JPEG."""
    uid = '1.2.840.10008.1.2.4.50'

    def test_pixel_array(self):
        index = get_indexed_datasets(self.uid)
        ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID

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


@pytest.mark.skipif(not RUN_JPEGLS, reason="No JPEG-LS plugin")
class TestJPEGLSPlugin:
    """Test interaction with plugins that support JPEG-LS."""
    uid = '1.2.840.10008.1.2.4.80'

    def test_pixel_array(self):
        index = get_indexed_datasets(self.uid)
        ds = index['MR_small_jpeg_ls_lossless.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'int16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        # Reference values from GDCM handler
        assert [1194,  879,  127,  661, 1943, 1885, 1857, 1746, 1699] == (
            arr[55:65, 38].tolist()
        )


@pytest.mark.skipif(not RUN_JPEG2K, reason="No JPEG 2000 plugin")
class TestJPEG2KPlugin:
    """Test interaction with plugins that support JPEG 2000."""
    uid = '1.2.840.10008.1.2.4.90'

    def test_pixel_array(self):
        index = get_indexed_datasets(self.uid)
        ds = index['US1_J2KR.dcm']['ds']

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns, ds.SamplesPerPixel) == arr.shape

        # Values checked against GDCM
        assert [
            [180,  26,   0],
            [172,  15,   0],
            [162,   9,   0],
            [152,   4,   0],
            [145,   0,   0],
            [132,   0,   0],
            [119,   0,   0],
            [106,   0,   0],
            [ 87,   0,   0],
            [ 37,   0,   0],
            [  0,   0,   0],
            [ 50,   0,   0],
            [100,   0,   0],
            [109,   0,   0],
            [122,   0,   0],
            [135,   0,   0],
            [145,   0,   0],
            [155,   5,   0],
            [165,  11,   0],
            [175,  17,   0]] == arr[175:195, 28, :].tolist()

    # FIXME
    def test_pixel_representation_mismatch(self):
        """Test mismatch between Pixel Representation and the J2K data."""
        index = get_indexed_datasets(self.uid)
        ds = index['J2K_pixelrep_mismatch.dcm']['ds']

        msg = (
            r"value '1' \(signed\) in the dataset does not match the format "
            r"of the values found in the JPEG 2000 data 'unsigned'"
        )
        with pytest.warns(UserWarning, match=msg):
            arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'int16' == arr.dtype
        assert (512, 512) == arr.shape

        assert -2000 == arr[0, 0]
        assert [621, 412, 138, -193, -520, -767, -907, -966, -988, -995] == (
            arr[47:57, 279].tolist()
        )
        assert [-377, -121, 141, 383, 633, 910, 1198, 1455, 1638, 1732] == (
            arr[328:338, 106].tolist()
        )


# Deprecated
class TestPydicomUtils:
    """Test the pydicom.utils functions."""
    @pytest.mark.skipif(not RUN_JPEG2K, reason="No JPEG 2000 plugin")
    def test_generate_frames_single_1s(self):
        """Test with single frame, 1 sample/px."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.90')
        ds = index['693_J2KR.dcm']['ds']
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 1 == ds.SamplesPerPixel
        frame_gen = generate_frames(ds)
        arr = next(frame_gen)
        with pytest.raises(StopIteration):
            next(frame_gen)

        assert arr.flags.writeable
        assert 'int16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape
        assert (
            [1022, 1051, 1165, 1442, 1835, 2096, 2074, 1868, 1685, 1603] ==
            arr[290, 135:145].tolist()
        )

    @pytest.mark.skipif(not RUN_JPEG2K, reason="No JPEG 2000 plugin")
    def test_generate_frames_1s(self):
        """Test with multiple frames, 1 sample/px."""
        index = get_indexed_datasets('1.2.840.10008.1.2.4.90')
        ds = index['emri_small_jpeg_2k_lossless.dcm']['ds']
        assert ds.NumberOfFrames > 1
        assert 1 == ds.SamplesPerPixel
        frames = generate_frames(ds)
        arr = next(frames)

        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape
        assert 163 == arr[12, 23]

    @pytest.mark.skipif(not RUN_JPEG, reason="No JPEG plugin")
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


# Deprecated
class TestGetJ2KParameters:
    """Tests for get_j2k_parameters."""
    def test_parameters(self):
        """Test getting the parameters for a JPEG2K codestream."""
        base = b'\xff\x4f\xff\x51' + b'\x00' * 38
        # Signed
        for ii in range(135, 143):
            params = get_j2k_parameters(base + bytes([ii]))
            assert ii - 127 == params['precision']
            assert params['is_signed']

        # Unsigned
        for ii in range(7, 17):
            params = get_j2k_parameters(base + bytes([ii]))
            assert ii + 1 == params['precision']
            assert not params['is_signed']

    def test_not_j2k(self):
        """Test result when no JPEG2K SOF marker present"""
        base = b'\xff\x4e\xff\x51' + b'\x00' * 38
        assert {} == get_j2k_parameters(base + b'\x8F')

    def test_no_siz(self):
        """Test result when no SIZ box present"""
        base = b'\xff\x4f\xff\x52' + b'\x00' * 38
        assert {} == get_j2k_parameters(base + b'\x8F')

    def test_short_bytestream(self):
        """Test result when no SIZ box present"""
        assert {} == get_j2k_parameters(b'')
        assert {} == get_j2k_parameters(b'\xff\x4f\xff\x51' + b'\x00' * 20)
