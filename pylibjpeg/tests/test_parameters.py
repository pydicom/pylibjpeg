"""Tests for the pylibjpeg pixel data handler."""

from io import BytesIO
import os
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

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(TEST_DIR, '../data')
DIR_10918 = os.path.join(DATA_DIR, 'jpg', '10918')
DIR_14495 = os.path.join(DATA_DIR, 'jpg', '14495')


REF_DCM = {
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


def test_get_parameters_bytes():
    """Test get_parameters() using bytes."""
    with open(os.path.join(DIR_10918, 'p1', 'A1.JPG'), 'rb') as fp:
        data = fp.read()

    params = get_parameters(data)

    info = (257, 255, 4, 8)

    assert (info[0], info[1]) == (params['rows'], params['columns'])
    assert info[2] == params['samples_per_pixel']
    assert info[3] == params['bits_per_sample']


@pytest.mark.skipif(not HAS_PYDICOM, reason="No pydicom")
def test_non_conformant_raises():
    """Test that a non-conformant JPEG image raises an exception."""
    ds_list = get_indexed_datasets('1.2.840.10008.1.2.4.51')
    # Image has invalid Se value in the SOS marker segment
    item = ds_list['JPEG-lossy.dcm']
    assert 0xC000 == item['Status'][1]
    ds = item['ds']

    nr_frames = ds.get('NumberOfFrames', 1)
    frame = next(generate_pixel_data_frame(ds.PixelData, nr_frames))

    msg = (
        r"libjpeg error code '-1038' returned from GetJPEGParameters\(\): A "
        r"misplaced marker segment was found - scan start must be zero "
        r"and scan stop must be 63 for the sequential operating modes"
    )
    with pytest.raises(RuntimeError, match=msg):
        get_parameters(frame)


@pytest.mark.skip("Not sure how to trigger exception")
def test_unknown_error_raised():
    """Test that an unknown error is handled properly."""
    #get_parameters(b'')
    pass


@pytest.mark.skipif(not HAS_PYDICOM, reason="No pydicom")
class TestGetParametersDCM(object):
    """Tests for get_parameters() using DICOM datasets."""
    def generate_frames(self, ds):
        """Return a generator object with the dataset's pixel data frames."""
        nr_frames = ds.get('NumberOfFrames', 1)
        return generate_pixel_data_frame(ds.PixelData, nr_frames)

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.50'])
    def test_baseline(self, fname, info):
        """Test get_parameters() for the baseline datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.51'])
    def test_extended(self, fname, info):
        """Test get_parameters() for the baseline datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.51')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.57'])
    def test_lossless(self, fname, info):
        """Test get_parameters() for the lossless datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.57')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.70'])
    def test_lossless_sv1(self, fname, info):
        """Test get_parameters() for the lossless SV1 datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.70')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.80'])
    def test_extended(self, fname, info):
        """Test get_parameters() for the LS lossless datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.80')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.81'])
    def test_extended(self, fname, info):
        """Test get_parameters() for the LS lossy datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.81')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        params = get_parameters(np.frombuffer(frame, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']


REF_JPG = {
    '10918' : {
        'p1' : [
            ('A1.JPG', (257, 255, 4, 8)),
            #('B1.JPG', (1, 1, 1, 1)),
            #('B2.JPG', (1, 1, 1, 1)), missing DHT marker (its in B1.JPG)
        ],
        'p2' : [
            ('A1.JPG', (257, 255, 4, 8)),
            #('B1.JPG', ()),
            #('B2.JPG', ()), missing DHT (in B1)
            ('C1.JPG', (257, 255, 4, 8)),
            ('C2.JPG', (257, 255, 4, 8)),
        ],
        'p4' : [
            ('A1.JPG', (257, 255, 4, 8)),
            #('B1.JPG', ()),
            #('B2.JPG', ()),
            ('C1.JPG', (257, 255, 4, 8)),
            ('C2.JPG', (257, 255, 4, 8)),
            ('E1.JPG', (257, 255, 4, 12)),
            ('E2.JPG', (257, 255, 4, 12)),
        ],
        'p14' : [
            ('O1.JPG', (257, 255, 4, 8)),
            ('O2.JPG', (257, 255, 4, 16)),
        ],
    },
    '14495' : {
        'JLS' : [
            ('T8C0E0.JLS', (256, 256, 3, 8)),
            ('T8C0E3.JLS', (256, 256, 3, 8)),
            ('T8C1E0.JLS', (256, 256, 3, 8)),
            ('T8C1E3.JLS', (256, 256, 3, 8)),
            ('T8C2E0.JLS', (256, 256, 3, 8)),
            ('T8C2E3.JLS', (256, 256, 3, 8)),
            ('T8NDE0.JLS', (128, 128, 1, 8)),
            ('T8NDE3.JLS', (128, 128, 1, 8)),
            ('T8SSE0.JLS', (256, 256, 3, 8)),
            ('T8SSE3.JLS', (256, 256, 3, 8)),
            ('T16E0.JLS', (256, 256, 1, 12)),
            ('T16E3.JLS', (256, 256, 1, 12)),
        ],
        'JNL' : [],
    },
    '15444' : {},
}


class TestGetParametersJPG(object):
    """Tests for get_parameters() using JPEG compliance data."""
    @pytest.mark.parametrize("fname, info", REF_JPG['10918']['p1'])
    def test_baseline(self, fname, info):
        """Test get_parameters() for the baseline compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_10918, 'p1', fname), 'rb') as fp:
            data = fp.read()

        params = get_parameters(np.frombuffer(data, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REF_JPG['10918']['p2'])
    def test_extended_p2(self, fname, info):
        """Test get_parameters() for the extended p2 compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_10918, 'p2', fname), 'rb') as fp:
            data = fp.read()

        params = get_parameters(np.frombuffer(data, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REF_JPG['10918']['p4'])
    def test_extended_p4(self, fname, info):
        """Test get_parameters() for the extended p4 compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_10918, 'p4', fname), 'rb') as fp:
            data = fp.read()

        params = get_parameters(np.frombuffer(data, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REF_JPG['10918']['p14'])
    def test_lossless_p14(self, fname, info):
        """Test get_parameters() for the extended p14 compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_10918, 'p14', fname), 'rb') as fp:
            data = fp.read()

        params = get_parameters(np.frombuffer(data, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']

    @pytest.mark.parametrize("fname, info", REF_JPG['14495']['JLS'])
    def test_jls(self, fname, info):
        """Test get_parameters() for the JPEG-LS compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_14495, 'JLS', fname), 'rb') as fp:
            data = fp.read()

        params = get_parameters(np.frombuffer(data, 'uint8'))

        assert (info[0], info[1]) == (params['rows'], params['columns'])
        assert info[2] == params['samples_per_pixel']
        assert info[3] == params['bits_per_sample']
