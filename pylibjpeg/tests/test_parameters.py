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
