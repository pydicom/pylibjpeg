"""Tests for pylibjpeg.decode()."""

from io import BytesIO
import os
import pytest
import warnings

import numpy as np

try:
    import pydicom
    from pydicom.encaps import generate_pixel_data_frame
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False

from pylibjpeg import add_handler, remove_handler, decode
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


# TODO: convert to using straight JPG data
@pytest.mark.skipif(not HAS_PYDICOM, reason="No pydicom")
def test_decode_bytes():
    """Test decode using bytes."""
    index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
    ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
    nr_frames = ds.get('NumberOfFrames', 1)
    frame = next(generate_pixel_data_frame(ds.PixelData, nr_frames))
    arr = decode(frame)
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


# TODO: convert to using straight JPG data
@pytest.mark.skipif(not HAS_PYDICOM, reason="No pydicom")
def test_invalid_colourspace_warns():
    """Test that using an unknown colourspace gives a warning."""
    index = get_indexed_datasets('1.2.840.10008.1.2.4.50')
    ds = index['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
    nr_frames = ds.get('NumberOfFrames', 1)
    frame = next(generate_pixel_data_frame(ds.PixelData, nr_frames))
    msg = (
        r""
    )
    with pytest.warns(UserWarning, match=msg):
        arr = decode(np.frombuffer(frame, 'uint8'), colourspace='ANY')

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


@pytest.mark.skipif(not HAS_PYDICOM, reason="No pydicom")
class TestDecodeDCM(object):
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
        arr = decode(np.frombuffer(frame, 'uint8'), reshape=True)

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.51'])
    def test_extended(self, fname, info):
        """Test get_parameters() for the baseline datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.51')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        arr = decode(np.frombuffer(frame, 'uint8'), reshape=True)

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.57'])
    def test_lossless(self, fname, info):
        """Test get_parameters() for the lossless datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.57')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        arr = decode(np.frombuffer(frame, 'uint8'), reshape=True)

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.70'])
    def test_lossless_sv1(self, fname, info):
        """Test get_parameters() for the lossless SV1 datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.70')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        arr = decode(np.frombuffer(frame, 'uint8'), reshape=True)

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.80'])
    def test_extended(self, fname, info):
        """Test get_parameters() for the LS lossless datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.80')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        arr = decode(np.frombuffer(frame, 'uint8'), reshape=True)

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'

    @pytest.mark.parametrize("fname, info", REF_DCM['1.2.840.10008.1.2.4.81'])
    def test_extended(self, fname, info):
        """Test get_parameters() for the LS lossy datasets."""
        #info: (rows, columns, spp, bps)
        index = get_indexed_datasets('1.2.840.10008.1.2.4.81')
        ds = index[fname]['ds']

        frame = next(self.generate_frames(ds))
        arr = decode(np.frombuffer(frame, 'uint8'), reshape=True)

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'


REF_JPG = {
    '10918' : {
        # Reference values using libjpeg's `jpeg` app + imageJ
        # Very circular but having issues with other programs interpreting
        #   it as CYMK and doing weird stuff
        'p1' : [
            # ([top left pixel], [bottom right pixel])
            (
                'A1.JPG', (257, 255, 4, 8),
                ([138, 76, 239, 216], [155, 217, 191, 115])
            ),
            #('B1.JPG', (1, 1, 1, 1)),
            #('B2.JPG', (1, 1, 1, 1)), missing DHT marker (its in B1.JPG)
        ],
        'p2' : [
            (
                'A1.JPG', (257, 255, 4, 8),
                ([138, 76, 239, 216], [155, 217, 191, 115])
            ),
            #('B1.JPG', ()),
            #('B2.JPG', ()), missing DHT (in B1)
            (
                'C1.JPG', (257, 255, 4, 8),
                ([138, 76, 239, 216], [155, 217, 191, 115])
            ),
            (
                'C2.JPG', (257, 255, 4, 8),
                ([138, 76, 239, 216], [155, 217, 191, 115])
            ),
        ],
        'p4' : [
            (
                'A1.JPG', (257, 255, 4, 8),
                ([138, 76, 239, 216], [155, 217, 191, 115])
            ),
            #('B1.JPG', ()),
            #('B2.JPG', ()),
            (
                'C1.JPG', (257, 255, 4, 8),
                ([138, 76, 239, 216], [155, 217, 191, 115])
            ),
            (
                'C2.JPG', (257, 255, 4, 8),
                ([138, 76, 239, 216], [155, 217, 191, 115])
            ),
            (
                'E1.JPG', (257, 255, 4, 12),
                ([2119, 1183, 3907, 3487], [2502, 3402, 3041, 1872])
            ),
            (
                'E2.JPG', (257, 255, 4, 12),
                ([2119, 1183, 3907, 3487], [2502, 3402, 3041, 1872])
            ),
        ],
        'p14' : [
            (
                'O1.JPG', (257, 255, 4, 8),
                ([132, 76, 245, 218], [156, 211, 191, 116])
            ),
            (
                'O2.JPG', (257, 255, 4, 16),
                ([33792, 19456, 62720, 55808], [39936, 53888, 48768, 29696])
            ),
        ],
    },
    '14495' : {
        'JLS' : [  # Lossless
            (
                # Reference values using GDCM
                'T8C0E0.JLS', (256, 256, 3, 8),
                ([161, 122, 108], [101, 99, 95])
            ),
            (
                # GDCM and CharPyLS fail on this one - both use CharLS
                 # Circular reference
                'T8C1E0.JLS', (256, 256, 3, 8),
                ([161, 122, 108], [101, 99, 95])
            ),
            (
                # CharLS fails
                # Circular reference
                'T8C2E0.JLS', (256, 256, 3, 8),
                ([161, 122, 108], [101, 99, 95])
            ),
            (
                # Reference values using GDCM
                'T8NDE0.JLS', (128, 128, 1, 8),
                (108, 231)
            ),
            (
                # CharLS fails
                # Circular reference
                'T8SSE0.JLS', (256, 256, 3, 8),
                ([161, 122, 108], [101, 171, 231])
            ),
            (
                # Reference values using GDCM
                'T16E0.JLS', (256, 256, 1, 12),
                (1963, 1596)
            ),
        ],
        'JNL' : [  # Near lossless
            (
                # Reference values using GDCM
                'T8C0E3.JLS', (256, 256, 3, 8),
                ([161, 119, 105], [98, 96, 93])
            ),
            (
                # CharLS fails
                # Circular reference
                'T8C1E3.JLS', (256, 256, 3, 8),
                ([161, 119, 105], [101, 100, 97])
            ),
            (
                # CharLS fails
                # Circular reference
                'T8C2E3.JLS', (256, 256, 3, 8),
                ([161, 119, 105], [98, 96, 94])
            ),
            (
                # Reference values using GDCM
                'T8NDE3.JLS', (128, 128, 1, 8),
                (105, 229)
            ),
            (
                # CharLS fails
                # Circular reference
                'T8SSE3.JLS', (256, 256, 3, 8),
                ([161, 119, 105], [102, 169, 234])
            ),
            (
                # Reference values using GDCM
                'T16E3.JLS', (256, 256, 1, 12),
                (1960, 1593)
            ),
        ],
    },
    '15444' : {},
}


class TestDecodeJPG(object):
    """Tests for get_parameters() using JPEG compliance data."""
    @pytest.mark.parametrize("fname, info, ref", REF_JPG['10918']['p1'])
    def test_baseline(self, fname, info, ref):
        """Test decoding the baseline compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_10918, 'p1', fname), 'rb') as fp:
            data = fp.read()

        arr = decode(np.frombuffer(data, 'uint8'), reshape=True)
        assert arr.flags.writeable

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        # Process 1 is always 8-bit
        assert arr.dtype == 'uint8'

        assert ref[0] == arr[0, 0, :].tolist()
        assert ref[1] == arr[-1, -1, :].tolist()

    @pytest.mark.parametrize("fname, info, ref", REF_JPG['10918']['p2'])
    def test_extended_p2(self, fname, info, ref):
        """Test decoding the extended p2 compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_10918, 'p2', fname), 'rb') as fp:
            data = fp.read()

        arr = decode(np.frombuffer(data, 'uint8'), reshape=True)
        assert arr.flags.writeable

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        # Process 2 is always 8-bit
        assert arr.dtype == 'uint8'

        assert ref[0] == arr[0, 0, :].tolist()
        assert ref[1] == arr[-1, -1, :].tolist()

    @pytest.mark.parametrize("fname, info, ref", REF_JPG['10918']['p4'])
    def test_extended_p4(self, fname, info, ref):
        """Test decoding the extended p4 compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_10918, 'p4', fname), 'rb') as fp:
            data = fp.read()

        arr = decode(np.frombuffer(data, 'uint8'), reshape=True)
        assert arr.flags.writeable

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'

        assert ref[0] == arr[0, 0, :].tolist()
        assert ref[1] == arr[-1, -1, :].tolist()

    @pytest.mark.parametrize("fname, info, ref", REF_JPG['10918']['p14'])
    def test_lossless_p14(self, fname, info, ref):
        """Test decoding the extended p14 compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_10918, 'p14', fname), 'rb') as fp:
            data = fp.read()

        arr = decode(np.frombuffer(data, 'uint8'), reshape=True)
        assert arr.flags.writeable

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'

        assert ref[0] == arr[0, 0, :].tolist()
        assert ref[1] == arr[-1, -1, :].tolist()

    @pytest.mark.parametrize("fname, info, ref", REF_JPG['14495']['JLS'])
    def test_jls(self, fname, info, ref):
        """Test decoding the JPEG-LS lossless compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_14495, 'JLS', fname), 'rb') as fp:
            data = fp.read()

        arr = decode(
            np.frombuffer(data, 'uint8'),
            reshape=True,
        )
        assert arr.flags.writeable

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'

        if info[2] == 1:
            assert ref[0] == arr[0, 0].tolist()
            assert ref[1] == arr[-1, -1].tolist()
        else:
            assert ref[0] == arr[0, 0, :].tolist()
            assert ref[1] == arr[-1, -1, :].tolist()

    @pytest.mark.parametrize("fname, info, ref", REF_JPG['14495']['JNL'])
    def test_jnl(self, fname, info, ref):
        """Test decoding the JPEG-LS near lossless compliance images."""
        #info: (rows, columns, spp, bps)
        with open(os.path.join(DIR_14495, 'JNL', fname), 'rb') as fp:
            data = fp.read()

        arr = decode(np.frombuffer(data, 'uint8'), reshape=True)
        assert arr.flags.writeable

        if info[2] == 1:
            assert (info[0], info[1]) == arr.shape
        else:
            assert (info[0], info[1], info[2]) == arr.shape

        if 1 <= info[3] <= 8:
            assert arr.dtype == 'uint8'
        if 9 <= info[3] <= 16:
            assert arr.dtype == 'uint16'

        if info[2] == 1:
            assert ref[0] == arr[0, 0].tolist()
            assert ref[1] == arr[-1, -1].tolist()
        else:
            assert ref[0] == arr[0, 0, :].tolist()
            assert ref[1] == arr[-1, -1, :].tolist()
