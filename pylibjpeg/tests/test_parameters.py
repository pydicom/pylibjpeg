"""Tests for the pylibjpeg pixel data handler."""

import pytest
import warnings

try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False

try:
    import pydicom
    import pydicom.config
    from pydicom.pixel_data_handlers.util import convert_color_space
    from pydicom.encaps import defragment_data, generate_pixel_data_frame
    from pylibjpeg import libjpeg_handler
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False

from pylibjpeg import add_handler, remove_handler, get_parameters
from pylibjpeg.data import get_indexed_datasets


REFERENCE = {
    '1.2.840.10008.1.2.4.50' : [
        # filename, (rows, columns, samples/px, bits/sample)
        ('JPEGBaseline_1s_1f_u_08_08.dcm', (100, 100, 1, 8)),
        ('SC_rgb_dcmtk_+eb+cy+np.dcm', (100, 100, 3, 8)),
        ('color3d_jpeg_baseline.dcm', (480, 640, 3, 8)),
        ('SC_rgb_dcmtk_+eb+cr.dcm', (100, 100, 3, 8)),
        ('SC_rgb_dcmtk_+eb+cy+n1.dcm', (100, 100, 3, 8)),
        ('SC_rgb_dcmtk_+eb+cy+s4.dcm', (100, 100, 3, 8)),
    ],
    '1.2.840.10008.1.2.4.51' : [
        ('RG2_JPLY_fixed.dcm', (2140, 1760, 1, 12)),
        ('JPEGExtended_1s_1f_u_16_12.dcm', (1024, 256, 1, 12)),
        ('JPEGExtended_3s_1f_u_08_08.dcm', (576, 768, 3, 8)),
    ],
    '1.2.840.10008.1.2.4.57' : [
        ('JPEGLossless_1s_1f_u_16_12.dcm', (1024, 1024, 1, 12)),
    ],
    '1.2.840.10008.1.2.4.70' : [
        ('JPEG-LL.dcm', (1024, 256, 1, 16)),
        ('JPEGLosslessP14SV1_1s_1f_u_08_08.dcm', (768, 1024, 1, 8)),
        ('JPEGLosslessP14SV1_1s_1f_u_16_16.dcm', (535, 800, 1, 16)),
        ('MG1_JPLL.dcm', (4664, 3064, 1, 12)),
        ('RG1_JPLL.dcm', (1955, 1841, 1, 15)),
        ('RG2_JPLL.dcm', (2140, 1760, 1, 10)),
        ('SC_rgb_jpeg_gdcm.dcm', (100, 100, 3, 8)),
    ],
    '1.2.840.10008.1.2.4.80' : [
        ('emri_small_jpeg_ls_lossless.dcm', (64, 64, 1, 12)),
        ('MR_small_jpeg_ls_lossless.dcm', (64, 64, 1, 16)),
        ('RG1_JLSL.dcm', (1955, 1841, 1, 16)),
        ('RG2_JLSL.dcm', (2140, 1760, 1, 10)),
    ],
    '1.2.840.10008.1.2.4.81' : [
        ('CT1_JLSN.dcm', (512, 512, 1, 16)),
        ('MG1_JLSN.dcm', (4664, 3064, 1, 12)),
        ('RG1_JLSN.dcm', (1955, 1841, 1, 15)),
        ('RG2_JLSN.dcm', (2140, 1760, 1, 10)),
    ],
}


# ISO/IEC 10918 JPEG
@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestGetParameters(object):
    """Tests for get_parameters()."""
    def generate_frames(self, ds):
        nr_frames = ds.get('NumberOfFrames', 1)
        return generate_pixel_data_frame(ds.PixelData, nr_frames)

    @pytest.mark.parametrize("fname, info", REFERENCE['1.2.840.10008.1.2.4.50'])
    def test_baseline(self, fname, info):
        """Test get_parameters() for the baseline datasets."""
        #info: (marker, rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REFERENCE['1.2.840.10008.1.2.4.51'])
    def test_extended(self, fname, info):
        """Test get_parameters() for the baseline datasets."""
        #info: (marker, rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.51')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REFERENCE['1.2.840.10008.1.2.4.57'])
    def test_lossless(self, fname, info):
        """Test get_parameters() for the lossless datasets."""
        #info: (marker, rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.57')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REFERENCE['1.2.840.10008.1.2.4.70'])
    def test_lossless_sv1(self, fname, info):
        """Test get_parameters() for the lossless SV1 datasets."""
        #info: (marker, rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.70')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REFERENCE['1.2.840.10008.1.2.4.80'])
    def test_extended(self, fname, info):
        """Test get_parameters() for the LS lossless datasets."""
        #info: (marker, rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.80')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REFERENCE['1.2.840.10008.1.2.4.81'])
    def test_extended(self, fname, info):
        """Test get_parameters() for the LS lossy datasets."""
        #info: (marker, rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.81')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']
