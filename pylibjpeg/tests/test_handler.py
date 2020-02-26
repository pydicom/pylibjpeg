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
    from pydicom.encaps import defragment_data
    from pylibjpeg import libjpeg_handler
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False

from pylibjpeg import add_handler, remove_handler, decode
from pylibjpeg.data import get_indexed_datasets


@pytest.mark.skipif(not HAS_PYDICOM, reason="pydicom unavailable")
def test_add_handler():
    """Test adding the handler to pydicom."""
    assert libjpeg_handler not in pydicom.config.pixel_data_handlers
    add_handler()
    assert libjpeg_handler in pydicom.config.pixel_data_handlers

    pydicom.config.pixel_data_handlers.remove(libjpeg_handler)


@pytest.mark.skipif(not HAS_PYDICOM, reason="pydicom unavailable")
def test_remove_handler():
    """Test removing the handler from pydicom."""
    add_handler()
    assert libjpeg_handler in pydicom.config.pixel_data_handlers
    remove_handler()
    assert libjpeg_handler not in pydicom.config.pixel_data_handlers


@pytest.mark.skipif(HAS_PYDICOM, reason="pydicom available")
def test_add_handler_raises():
    """Test adding the handler raises if no pydicom."""
    with pytest.raises(ImportError):
        add_handler()


@pytest.mark.skipif(HAS_PYDICOM, reason="pydicom available")
def test_remove_handler_raises():
    """Test removing the handler raises if no pydicom."""
    with pytest.raises(ImportError):
        remove_handler()


class HandlerTestBase(object):
    """Baseclass for handler tests."""
    uid = None

    def setup(self):
        add_handler()
        self.ds = get_indexed_datasets(self.uid)

    def teardown(self):
        remove_handler()

    def plot(self, arr, index=None, cmap=None):
        import matplotlib.pyplot as plt

        if index is not None:
            if cmap:
                plt.imshow(arr[index], cmap=cmap)
            else:
                plt.imshow(arr[index])
        else:
            if cmap:
                plt.imshow(arr, cmap=cmap)
            else:
                plt.imshow(arr)

        plt.show()


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestLibrary(object):
    """Tests for libjpeg itself."""
    def setup(self):
        add_handler()

    def teardown(self):
        remove_handler()

    def test_non_conformant_raises(self):
        """Test that a non-conformant JPEG image raises an exception."""
        ds_list = get_indexed_datasets('1.2.840.10008.1.2.4.51')
        # Image has invalid Se value in the SOS marker segment
        item = ds_list['JPEG-lossy.dcm']
        assert 0xC000 == item['Status'][1]
        msg = (
            r"libjpeg error code '-1038' returned from Decode\(\): A "
            r"misplaced marker segment was found - scan start must be zero "
            r"and scan stop must be 63 for the sequential operating modes"
        )
        with pytest.raises(RuntimeError, match=msg):
            arr = item['ds'].pixel_array

    def test_invalid_colour_transform(self):
        """Test that an invalid colour transform raises an exception."""
        ds_list = get_indexed_datasets('1.2.840.10008.1.2.4.50')
        # Image has invalid Se value in the SOS marker segment
        ds = ds_list['color3d_jpeg_baseline.dcm']['ds']
        data = defragment_data(ds.PixelData)
        msg = (
            r"Unsupported colour space '-1', no colour transform will "
            r"be applied"
        )
        with pytest.warns(UserWarning, match=msg):
            decode(np.frombuffer(data, 'uint8'), 1, -1)

    def test_invalid_buffer(self):
        """Test that an invalid colour transform raises an exception."""
        msg = (
            r"Buffer dtype mismatch, expected 'uint8_t' but got 'double'"
        )
        with pytest.raises(ValueError, match=msg):
            decode(np.zeros(1), 1, 'YBR_FULL')


# ISO/IEC 10918 JPEG
@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGBaseline(HandlerTestBase):
    """Test the handler with ISO 10918 JPEG images.

    1.2.840.10008.1.2.4.50 : JPEG Baseline (Process 1)

    Process 1: Baseline sequential DCT, 8-bit sample precision.

    Image samples assumed to be unsigned in the range 0 to 255.

    Supported Values
    ----------------
    Photometric Interpretation: MONOCHROME1, MONOCHROME2, YBR_FULL_422
    Samples Per Pixel: 1 or 3
    Planar Configuration: 0 (for YBR_FULL_422)
    Pixel Representation: 0 (unsigned)
    Bits Allocated/Stored: 8/8

    References
    ----------
    * :dcm:`DICOM Standard, Part 5, Table 8.2.1-1
      <part05/sect_8.2.html#table_8.2.1-1>`
    * ISO/IEC 10918-1 (ITU T.81)
    * ISO/IEC 10918-2
    * `JPEG Image Compression Systems
      <https://www.ece.ucdavis.edu/cerl/reliablejpeg/compression/>`_

    Missing datasets
    ----------------
    1 sample/px, 8/8 bits allocated/stored, unsigned, > 1 frame
    """
    uid = '1.2.840.10008.1.2.4.50'

    def test_1s_1f(self):
        """Test greyscale."""
        ds = self.ds['JPEGBaseline_1s_1f_u_08_08.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr, cmap='gray')

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

    @pytest.mark.skip('No suitable dataset')
    def test_1s_Nf(self):
        """Test greyscale with N frames."""
        ds = self.ds['JPEGBaseline_1s_2f_08_08.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 2 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (2, ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr, index=0, cmap='gray')

    def test_3s_1f_ybr_422(self):
        """Test YBR with 422 subsampling."""
        # +cy is YCbCr
        # +s2 is 422 subsampling w/ YBR_FULL_422
        ds = self.ds['SC_rgb_dcmtk_+eb+cy+np.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 3 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'YBR_FULL_422' == ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns, 3) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler - slightly different
        assert ( 76,  85, 254) == tuple(arr[ 5, 50, :])
        # assert (166, 109, 190) == tuple(arr[15, 50, :])
        assert (166, 108, 190) == tuple(arr[15, 50, :])  # Different
        assert (150,  46,  21) == tuple(arr[25, 50, :])
        # assert (203,  85,  74) == tuple(arr[35, 50, :])
        assert (203,  86,  74) == tuple(arr[35, 50, :])  # Different
        # assert ( 29, 255, 108) == tuple(arr[45, 50, :])
        assert ( 29, 255, 107) == tuple(arr[45, 50, :])  # Different
        assert (142, 192, 117) == tuple(arr[55, 50, :])
        assert (  0, 128, 128) == tuple(arr[65, 50, :])
        assert ( 64, 128, 128) == tuple(arr[75, 50, :])
        assert (192, 128, 128) == tuple(arr[85, 50, :])
        assert (255, 128, 128) == tuple(arr[95, 50, :])

    def test_3s_Nf_ybr_422(self):
        """Test 3 sample/px with N frames."""
        ds = self.ds['color3d_jpeg_baseline.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 3 == ds.SamplesPerPixel
        assert 1 != getattr(ds, 'NumberOfFrames', 1)
        assert 8 == ds.BitsAllocated == ds.BitsStored
        assert 'YBR_FULL_422' == ds.PhotometricInterpretation
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.NumberOfFrames, ds.Rows, ds.Columns, 3) == arr.shape

        arr = convert_color_space(arr, 'YBR_FULL', 'RGB')

        #self.plot(arr, index=3)

        assert (41,  41,  41) == tuple(arr[3, 159, 290, :])
        assert (57,  57,  57) == tuple(arr[3, 169, 290, :])
        assert (72, 167, 125) == tuple(arr[3, 41, 380, :])

    # Non-conformant datasets
    def test_3s_1f_rgb_non(self):
        """Test RGB."""
        # +cr is RGB - DICOM non-conformant
        ds = self.ds['SC_rgb_dcmtk_+eb+cr.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 3 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'RGB' == ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns, 3) == arr.shape

        #self.plot(arr)

        assert (255,   0,   0) == tuple(arr[ 5, 50, :])
        assert (255, 128, 128) == tuple(arr[15, 50, :])
        assert (  0, 255,   0) == tuple(arr[25, 50, :])
        assert (128, 255, 128) == tuple(arr[35, 50, :])
        assert (  0,   0, 255) == tuple(arr[45, 50, :])
        assert (128, 128, 255) == tuple(arr[55, 50, :])
        assert (  0,   0,   0) == tuple(arr[65, 50, :])
        assert ( 64,  64,  64) == tuple(arr[75, 50, :])
        assert (192, 192, 192) == tuple(arr[85, 50, :])
        assert (255, 255, 255) == tuple(arr[95, 50, :])

    def test_3s_1f_ybr_411_non(self):
        """Test YBR with 411 subsampling."""
        # +cy is YCbCr
        # +n1 is 411 subsampling w/ YBR_FULL - DICOM non-conformant
        ds = self.ds['SC_rgb_dcmtk_+eb+cy+n1.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 3 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'YBR_FULL' == ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns, 3) == arr.shape

        arr = convert_color_space(arr, 'YBR_FULL', 'RGB')

        #self.plot(arr)

        assert (253,   1,   0) == tuple(arr[ 5, 50, :])
        assert (253, 129, 131) == tuple(arr[15, 50, :])
        assert (  0, 255,   5) == tuple(arr[25, 50, :])
        assert (127, 255, 129) == tuple(arr[35, 50, :])
        assert (  0,   0, 254) == tuple(arr[45, 50, :])
        assert (127, 128, 255) == tuple(arr[55, 50, :])
        assert (  0,   0,   0) == tuple(arr[65, 50, :])
        assert ( 64,  64,  64) == tuple(arr[75, 50, :])
        assert (192, 192, 192) == tuple(arr[85, 50, :])
        assert (255, 255, 255) == tuple(arr[95, 50, :])

    def test_3s_1f_ybr_444_non(self):
        """Test YBR with 444 subsampling."""
        # +cy is YCbCr
        # +s4 is 444 subsampling w/ YBR_FULL - DICOM non-conformant
        ds = self.ds['SC_rgb_dcmtk_+eb+cy+s4.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 3 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'YBR_FULL' == ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns, 3) == arr.shape

        arr = convert_color_space(arr, 'YBR_FULL', 'RGB')

        #self.plot(arr)

        assert (254,   0,   0) == tuple(arr[ 5, 50, :])
        assert (255, 127, 127) == tuple(arr[15, 50, :])
        assert (  0, 255,   5) == tuple(arr[25, 50, :])
        assert (129, 255, 129) == tuple(arr[35, 50, :])
        assert (  0,   0, 254) == tuple(arr[45, 50, :])
        assert (128, 127, 255) == tuple(arr[55, 50, :])
        assert (  0,   0,   0) == tuple(arr[65, 50, :])
        assert ( 64,  64,  64) == tuple(arr[75, 50, :])
        assert (192, 192, 192) == tuple(arr[85, 50, :])
        assert (255, 255, 255) == tuple(arr[95, 50, :])


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGExtended(HandlerTestBase):
    """Test the handler with ISO 10918 JPEG images.

    1.2.840.10008.1.2.4.51 : JPEG Extended (Process 2 and 4)

    Process 2: Extended sequential DCT, Huffman coding, 8-bit sample precision
    Process 4: Extended sequential DCT, Huffman coding, 12-bit sample precision

    Supported Values
    ----------------
    Photometric Interpretation: MONOCHROME1, MONOCHROME2
    Samples Per Pixel: 1
    Pixel Representation: 0 (unsigned)
    Bits Allocated/Stored: 8/8 or 16/12

    References
    ----------
    * :dcm:`DICOM Standard, Part 5, Table 8.2.1-1
      <part05/sect_8.2.html#table_8.2.1-1>`
    * ISO/IEC 10918-1 (ITU T.81)
    * ISO/IEC 10918-2
    * `JPEG Image Compression Systems
      <https://www.ece.ucdavis.edu/cerl/reliablejpeg/compression/>`_

    Missing datasets
    ----------------
    1 sample/px, 8/8 bits allocated/stored, unsigned, 1 frame
    1 sample/px, 8/8 bits allocated/stored, unsigned, > 1 frame
    1 sample/px, 16/12 bits allocated/stored, unsigned, > 1 frame
    """
    uid = '1.2.840.10008.1.2.4.51'

    # Process 2
    @pytest.mark.skip("No suitable dataset")
    def test_1s_1f_u_08_08(self):
        pass

    @pytest.mark.skip("No suitable dataset")
    def test_1s_Nf_u_08_08(self):
        pass

    # Process 4
    def test_1s_1f_u_16_10(self):
        """Test process 4 greyscale."""
        ds = self.ds['RG2_JPLY_fixed.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        # Input precision is 12, not 10
        assert 10 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from output of IJG's djpeg recompiled for 12-bit
        # Note differences       |              |
        # IJG: [571, 582, 666, 766, 803, 781, 726, 651, 595, 578]
        assert [571, 582, 666, 765, 803, 781, 725, 651, 595, 578] == (
            arr[845, 964:974].tolist()
        )

    def test_1s_1f_u_16_12(self):
        """Test process 4 greyscale."""
        ds = self.ds['JPEGExtended_1s_1f_u_16_12.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 12 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from output of IJG's djpeg recompiled for 12-bit
        # Note differences  |
        # IJG: [134, 143, 161, 172, 180, 193, 249, 214, 223, 247]
        assert [134, 143, 160, 172, 180, 193, 249, 214, 223, 247] == (
            arr[410:420, 136].tolist()
        )

    @pytest.mark.skip("No suitable dataset")
    def test_1s_Nf_u_16_12(self):
        pass

    # Non-conformant datasets
    def test_3s_1f_u_08_08_non(self):
        """Test process 2 greyscale."""
        # Non-conformant to DICOM
        ds = self.ds['JPEGExtended_3s_1f_u_08_08.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 3 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'YBR_FULL' in ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated
        assert 8 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns, 3) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler - in YBR colour space
        assert [
            [ 71,  86, 147],
            [124,  62, 167],
            [138,  66, 175],
            [145,  65, 172],
            [150,  59, 168],
            [178,  59, 167],
            [183,  56, 171],
            [201,  83, 165],
            [213,  92, 153],
            [255, 132, 134]
        ] == arr[41, 105:115].tolist()


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLossless(HandlerTestBase):
    """Test the handler with ISO 10918 JPEG images.

    1.2.840.10008.1.2.4.57 : JPEG Lossless, Non-Hierarchical (Process 14)

    Process 14: Lossless, Huffman coding, 2 to 16-bit sample precision

    Supported Values
    ----------------
    Photometric Interpretation: MONOCHROME1, MONOCHROME2, PALETTE COLOR,
        YBR_FULL, RGB
    Samples Per Pixel: 1 or 3
    Planar Configuration: 0 (for RGB/YBR_FULL)
    Pixel Representation: 0 (unsigned) or 1 (signed, monochrome only)
    Bits Allocated: 8 or 16
    Bits Stored: 1 to 16

    References
    ----------
    * :dcm:`DICOM Standard, Part 5, Table 8.2.1-2
      <part05/sect_8.2.html#table_8.2.1-2>`
    * ISO/IEC 10918-1 (ITU T.81)
    * ISO/IEC 10918-2
    * `JPEG Image Compression Systems
      <https://www.ece.ucdavis.edu/cerl/reliablejpeg/compression/>`_

    Missing datasets
    ----------------
    1 sample/px, 8/8 bits allocated/stored, signed, 1 frame
    1 sample/px, 8/8 bits allocated/stored, signed, > 1 frame
    1 sample/px, 8/8 bits allocated/stored, unsigned, > 1 frame
    1 sample/px, 16/xx bits allocated/stored, signed, 1 frame
    1 sample/px, 16/xx bits allocated/stored, signed, > 1 frame
    1 sample/px, 16/16 bits allocated/stored, signed, > 1 frame
    1 sample/px, 16/xx bits allocated/stored, unsigned, > 1 frame
    1 sample/px, 16/16 bits allocated/stored, unsigned, 1 frame
    1 sample/px, 16/16 bits allocated/stored, unsigned, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, PALETTE COLOR, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, PALETTE COLOR, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, YBR_FULL, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, YBR_FULL, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, RGB, > 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, PALETTE COLOR, 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, PALETTE COLOR, > 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, YBR_FULL, 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, YBR_FULL, > 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, YBR_FULL, 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, YBR_FULL, > 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, RGB, > 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, RGB, > 1 frame
    """
    uid = '1.2.840.10008.1.2.4.57'

    def test_1s_1f_u_08_08(self):
        """Test process 2 greyscale."""
        ds = self.ds['JPEGLossless_1s_1f_u_16_12.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 12 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler
        assert [392, 304, 238, 250, 224, 257, 221, 182, 166, 68] == (
            arr[779, 170:180].tolist()
        )


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLosslessSV1(HandlerTestBase):
    """Test the handler with ISO 10918 JPEG images.

    1.2.840.10008.1.2.4.70 : JPEG Lossless, Non-Hierarchical, First-Order
    Prediction (Process 14 [Selection Value 1]

    Process 14: Lossless, Huffman coding, 2 to 16-bit sample precision,
    selection value of 1

    Supported Values
    ----------------
    Photometric Interpretation: MONOCHROME1, MONOCHROME2, PALETTE COLOR,
        YBR_FULL, RGB
    Samples Per Pixel: 1 or 3
    Planar Configuration: 0 (for RGB/YBR_FULL)
    Pixel Representation: 0 (unsigned) or 1 (signed, monochrome only)
    Bits Allocated: 8 or 16
    Bits Stored: 1 to 16

    References
    ----------
    * :dcm:`DICOM Standard, Part 5, Table 8.2.1-2
      <part05/sect_8.2.html#table_8.2.1-2>`
    * ISO/IEC 10918-1 (ITU T.81)
    * ISO/IEC 10918-2
    * `JPEG Image Compression Systems
      <https://www.ece.ucdavis.edu/cerl/reliablejpeg/compression/>`_

    Missing datasets
    ----------------
    1 sample/px, 8/8 bits allocated/stored, signed, 1 frame
    1 sample/px, 8/8 bits allocated/stored, signed, > 1 frame
    1 sample/px, 8/8 bits allocated/stored, unsigned, > 1 frame
    1 sample/px, 16/xx bits allocated/stored, signed, 1 frame
    1 sample/px, 16/xx bits allocated/stored, signed, > 1 frame
    1 sample/px, 16/16 bits allocated/stored, signed, > 1 frame
    1 sample/px, 16/xx bits allocated/stored, unsigned, > 1 frame
    1 sample/px, 16/16 bits allocated/stored, unsigned, 1 frame
    1 sample/px, 16/16 bits allocated/stored, unsigned, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, PALETTE COLOR, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, PALETTE COLOR, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, YBR_FULL, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, YBR_FULL, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, RGB, > 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, PALETTE COLOR, 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, PALETTE COLOR, > 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, YBR_FULL, 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, YBR_FULL, > 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, YBR_FULL, 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, YBR_FULL, > 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, RGB, > 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, RGB, > 1 frame
    """
    uid = '1.2.840.10008.1.2.4.70'

    # 1 sample/px, 8/8
    def test_1s_1f_u_08_08(self):
        """Test process 2 greyscale."""
        ds = self.ds['JPEGLosslessP14SV1_1s_1f_u_08_08.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated
        assert 8 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler
        assert [0, 255, 254, 253, 253, 252, 251] == arr[121:128, 974].tolist()

    # 1 sample/px, 16/NN
    def test_1s_1f_u_16_10(self):
        """Test process 2 greyscale."""
        ds = self.ds['RG2_JPLL.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 10 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler
        assert [574, 669, 763, 782, 789, 736, 637, 583, 592, 589] == (
            arr[845, 965:975].tolist()
        )

    def test_1s_1f_u_16_12(self):
        """Test process 2 greyscale."""
        ds = self.ds['MG1_JPLL.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 12 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler
        assert [3023, 2862, 2841, 2825, 2841] == arr[1830:1835, 1285].tolist()

    def test_1s_1f_u_16_15(self):
        """Test process 2 greyscale."""
        ds = self.ds['RG1_JPLL.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 15 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler
        assert [24043, 23906, 23669, 23526, 22962, 22874, 22501, 22066] == (
            arr[1900, 1805:1813].tolist()
        )

    def test_1s_1f_i_16_16(self):
        """Test process 2 greyscale."""
        ds = self.ds['JPEG-LL.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 16 == ds.BitsStored
        assert 1 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'int16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        assert 227 == arr[420, 140]
        assert 105 == arr[230, 120]

    # 3 samples/px, 8/8
    def test_3s_1f_u_08_08_rgb(self):
        """Test process 2 greyscale."""
        ds = self.ds['SC_rgb_jpeg_gdcm.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 3 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'RGB' in ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated
        assert 8 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint8' == arr.dtype
        assert (ds.Rows, ds.Columns, 3) == arr.shape

        #self.plot(arr)

        assert (255,   0,   0) == tuple(arr[ 5, 50, :])
        assert (255, 128, 128) == tuple(arr[15, 50, :])
        assert (  0, 255,   0) == tuple(arr[25, 50, :])
        assert (128, 255, 128) == tuple(arr[35, 50, :])
        assert (  0,   0, 255) == tuple(arr[45, 50, :])
        assert (128, 128, 255) == tuple(arr[55, 50, :])
        assert (  0,   0,   0) == tuple(arr[65, 50, :])
        assert ( 64,  64,  64) == tuple(arr[75, 50, :])
        assert (192, 192, 192) == tuple(arr[85, 50, :])
        assert (255, 255, 255) == tuple(arr[95, 50, :])


# ISO/IEC 14495 JPEG-LS
@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLSLossless(HandlerTestBase):
    """Test the handler with ISO 14495 JPEG-LS images.

    1.2.840.10008.1.2.4.80 : JPEG-LS Lossless Image Compression

    Supported Values
    ----------------
    Photometric Interpretation: MONOCHROME1, MONOCHROME2, PALETTE COLOR,
        YBR_FULL, RGB
    Samples Per Pixel: 1 or 3
    Planar Configuration: 1 (for RGB/YBR_FULL)
    Pixel Representation: 0 (unsigned) or 1 (signed, monochrome only)
    Bits Allocated: 8 or 16
    Bits Stored: 2 to 16

    References
    ----------
    * :dcm:`DICOM Standard, Part 5, Table 8.2.3-1
      <part05/sect_8.2.html#table_8.2.3-1>`
    * ISO/IEC 14495

    Missing datasets
    ----------------
    1 sample/px, 8/8 bits allocated/stored, signed, 1 frame
    1 sample/px, 8/8 bits allocated/stored, signed, > 1 frame
    1 sample/px, 8/8 bits allocated/stored, unsigned, 1 frame
    1 sample/px, 8/8 bits allocated/stored, unsigned, > 1 frame
    1 sample/px, 16/xx bits allocated/stored, signed, 1 frame
    1 sample/px, 16/xx bits allocated/stored, signed, > 1 frame
    1 sample/px, 16/16 bits allocated/stored, signed, > 1 frame
    1 sample/px, 16/xx bits allocated/stored, unsigned, 1 frame
    1 sample/px, 16/16 bits allocated/stored, unsigned, 1 frame
    1 sample/px, 16/16 bits allocated/stored, unsigned, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, PALETTE COLOR, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, PALETTE COLOR, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, YBR_FULL, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, YBR_FULL, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, RGB, > 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, PALETTE COLOR, 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, PALETTE COLOR, > 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, RGB, > 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, RGB, > 1 frame
    """
    uid = '1.2.840.10008.1.2.4.80'

    def test_1s_1f_i_16_16(self):
        """Test process 2 greyscale."""
        ds = self.ds['MR_small_jpeg_ls_lossless.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 16 == ds.BitsStored
        assert 1 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'int16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr, cmap='gray')

        # Reference values from GDCM handler
        assert [1194,  879,  127,  661, 1943, 1885, 1857, 1746, 1699] == (
            arr[55:65, 38].tolist()
        )

    def test_1s_Nf_u_16_12(self):
        """Test process 2 greyscale."""
        ds = self.ds['emri_small_jpeg_ls_lossless.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 10 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 12 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (10, ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr, index=0, cmap='gray')

        # Reference values from GDCM handler
        assert [361, 295, 215,  98,  79,  70,  41,  29,  61,  64] == (
            arr[0, 18:28, 48].tolist()
        )
        assert [298, 332, 355, 361, 324, 263, 169, 105,  53,  45] == (
            arr[9, 18:28, 48].tolist()
        )


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLS(HandlerTestBase):
    """Test the handler with ISO 14495 JPEG-LS images.

    Transfer Syntaxes
    -----------------

    1.2.840.10008.1.2.4.81 : JPEG-LS Lossy (Near-Lossless) Image Compression

    Supported Values
    ----------------
    Photometric Interpretation: MONOCHROME1, MONOCHROME2, YBR_FULL, RGB
    Samples Per Pixel: 1 or 3
    Planar Configuration: 1 (for RGB/YBR_FULL)
    Pixel Representation: 0 (unsigned) or 1 (signed, monochrome only)
    Bits Allocated: 8 or 16
    Bits Stored: 2 to 16

    References
    ----------
    * :dcm:`DICOM Standard, Part 5, Table 8.2.3-1
      <part05/sect_8.2.html#table_8.2.3-1>`
    * ISO/IEC 14495

    Missing datasets
    ----------------
    1 sample/px, 8/8 bits allocated/stored, signed, 1 frame
    1 sample/px, 8/8 bits allocated/stored, signed, > 1 frame
    1 sample/px, 8/8 bits allocated/stored, unsigned, 1 frame
    1 sample/px, 8/8 bits allocated/stored, unsigned, > 1 frame
    1 sample/px, 16/xx bits allocated/stored, signed, 1 frame
    1 sample/px, 16/xx bits allocated/stored, signed, > 1 frame
    1 sample/px, 16/16 bits allocated/stored, signed, > 1 frame
    1 sample/px, 16/xx bits allocated/stored, unsigned, > 1 frame
    1 sample/px, 16/16 bits allocated/stored, unsigned, 1 frame
    1 sample/px, 16/16 bits allocated/stored, unsigned, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, YBR_FULL, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, YBR_FULL, > 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 8/8 bits allocated/stored, unsigned, RGB, > 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 16/xx bits allocated/stored, unsigned, RGB, > 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, RGB, 1 frame
    3 sample/px, 16/16 bits allocated/stored, unsigned, RGB, > 1 frame
    """
    uid = '1.2.840.10008.1.2.4.81'

    def test_1s_1f_i_16_16(self):
        """Test process 2 greyscale."""
        ds = self.ds['CT1_JLSN.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 16 == ds.BitsStored
        assert 1 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'int16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler
        assert [-2000, -2000, 936, 946, 927, 925, 918, 929, 931, 921] == (
            arr[433, 69:79].tolist()
        )

    def test_1s_1f_u_16_10(self):
        """Test process 2 greyscale."""
        ds = self.ds['RG2_JLSN.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 10 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler
        assert [574, 666, 760, 781, 789, 733, 634, 585, 594, 589] == (
            arr[845, 965:975].tolist()
        )

    def test_1s_1f_u_16_12(self):
        """Test process 2 greyscale."""
        ds = self.ds['MG1_JLSN.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 12 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler
        assert [3027, 2859, 2839, 2821, 2837, 2834, 2817, 2844, 2837] == (
            arr[1830:1839, 1285].tolist()
        )

    def test_1s_1f_u_16_15(self):
        """Test process 2 greyscale."""
        ds = self.ds['RG1_JLSN.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 15 == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'uint16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr)

        # Reference values from GDCM handler
        assert [24047, 23910, 23668, 23529, 22960, 22871, 22505, 22066] == (
            arr[1900, 1805:1813].tolist()
        )


# ISO/IEC 15444 JPEG 2000 - Expected fail
@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEG2000Lossless(HandlerTestBase):
    """Test the handler with ISO 15444 JPEG2000 images.

    1.2.840.10008.1.2.4.90 : JPEG 2000 Image Compression (Lossless Only)
    """
    uid = '1.2.840.10008.1.2.4.90'

    def setup(self):
        add_handler()
        self.ds = get_indexed_datasets(self.uid)

        # Check if J2K is already supported, and if not add it
        self.has_tsyntax = True
        if self.uid not in libjpeg_handler.SUPPORTED_TRANSFER_SYNTAXES:
            self.has_tsyntax = False
            libjpeg_handler.SUPPORTED_TRANSFER_SYNTAXES.append(self.uid)

    def teardown(self):
        remove_handler()

        # Restore J2K if it was originally supported
        if not self.has_tsyntax:
            libjpeg_handler.SUPPORTED_TRANSFER_SYNTAXES.remove(self.uid)

    def test_1s_1f_i_16_16(self):
        """Test process 2 greyscale."""
        ds = self.ds['693_J2KR.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 16 == ds.BitsStored
        assert 1 == ds.PixelRepresentation

        msg = (
            r"libjpeg error code '-1038' returned from Decode\(\): A "
            r"misplaced marker segment was found - stream does not contain a "
            r"JPEG file, SOI marker missing"
        )
        with pytest.raises(RuntimeError, match=msg):
            arr = ds.pixel_array


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEG2000(HandlerTestBase):
    """Test the handler with ISO 15444 JPEG2000 images.

    1.2.840.10008.1.2.4.91 : JPEG 2000 Image Compression
    """
    uid = '1.2.840.10008.1.2.4.91'

    def setup(self):
        add_handler()
        self.ds = get_indexed_datasets(self.uid)

        # Check if J2K is already supported, and if not add it
        self.has_tsyntax = True
        if self.uid not in libjpeg_handler.SUPPORTED_TRANSFER_SYNTAXES:
            self.has_tsyntax = False
            libjpeg_handler.SUPPORTED_TRANSFER_SYNTAXES.append(self.uid)

    def teardown(self):
        remove_handler()

        # Restore J2K if it was originally supported
        if not self.has_tsyntax:
            libjpeg_handler.SUPPORTED_TRANSFER_SYNTAXES.remove(self.uid)

    def test_1s_1f_i_16_16(self):
        """Test process 2 greyscale."""
        ds = self.ds['693_J2KI.dcm']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 14 == ds.BitsStored
        assert 1 == ds.PixelRepresentation

        msg = (
            r"libjpeg error code '-1038' returned from Decode\(\): A "
            r"misplaced marker segment was found - stream does not contain a "
            r"JPEG file, SOI marker missing"
        )
        with pytest.raises(RuntimeError, match=msg):
            arr = ds.pixel_array
