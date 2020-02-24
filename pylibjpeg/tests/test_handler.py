"""Tests for the pylibjpeg pixel data handler."""

import pytest

try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False

try:
    import pydicom
    import pydicom.config
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False

from pydicom.pixel_data_handlers.util import convert_color_space

from pylibjpeg import add_handler, remove_handler
from pylibjpeg import libjpeg_handler
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


# ISO/IEC 10918 JPEG
@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGBaseline(HandlerTestBase):
    """Test the handler with ISO 10918 JPEG images.

    1.2.840.10008.1.2.4.50 : JPEG Baseline (Process 1)

    Supported Elements
    ------------------
    Bits Allocated: 8
    Bits Stored: 8
    Samples Per Pixel: 1 or 3
    Number of Frames: N
    Photometric Interpretation: MONOCHROME1, MONOCHROME2, RGB, YBR_FULL,
        YBR_FULL_422
    """
    uid = '1.2.840.10008.1.2.4.50'

    @pytest.mark.skip("No matching dataset")
    def test_1s_1f(self):
        """Test greyscale."""
        ds = self.ds['']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array

        #self.plot(arr)

    @pytest.mark.skip("No matching dataset")
    def test_1s_Nf(self):
        """Test greyscale with N frames."""
        ds = self.ds['']['ds']
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 != getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 8 == ds.BitsAllocated == ds.BitsStored
        assert 0 == ds.PixelRepresentation

        arr = ds.pixel_array

        #self.plot(arr)

    def test_3s_1f_rgb(self):
        """Test RGB."""
        # +cr is RGB
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

    def test_3s_1f_ybr_411(self):
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

    def test_3s_1f_ybr_444(self):
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

    def test_3s_Nf(self):
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


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGExtended(HandlerTestBase):
    """Test the handler with ISO 10918 JPEG images.

    1.2.840.10008.1.2.4.51 : JPEG Extended (Process 2 and 4)

    Supported Elements
    ------------------
    Bits Allocated: 8 (for Process 2) or 16 (for Process 4)
    Bits Stored: 8 (for Process 2) or 12 (for Process 4)
    Samples Per Pixel: 1 or 3
    Number of Frames: N
    Photometric Interpretation: MONOCHROME1, MONOCHROME2, RGB, YBR_FULL,
        YBR_FULL_422
    """
    uid = '1.2.840.10008.1.2.4.51'

    @pytest.mark.skip("No matching dataset")
    def test_p2_1s_1f(self):
        """Test process 2 greyscale."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p2_1s_2f(self):
        """Test process 2 greyscale with 2 frames."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p2_3s_1f_rgb(self):
        """Test process 2 RGB."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p2_3s_1f_ybr_411(self):
        """Test process 2 YBR with 411 subsampling."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p2_3s_1f_ybr_422(self):
        """Test process 2 YBR with 422 subsampling."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p2_3s_1f_ybr_444(self):
        """Test process 2 YBR with 444 subsampling."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p2_3s_2f(self):
        """Test process 2 3 sample/px with 2 frames."""
        pass

    # Needs reference data
    def test_p4_1s_1f_u_16_12(self):
        """Test process 4 greyscale."""
        ds = self.ds['JPGExtended_1s_1f_16_12.dcm']['ds']
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

    @pytest.mark.skip("No matching dataset")
    def test_p4_1s_2f(self):
        """Test process 4 greyscale with 2 frames."""
        pass

    # Needs reference data
    def test_p4_1s_1f_u_16_10(self):
        """Test process 4 greyscale."""
        ds = self.ds['RG2_JPLY']['ds']
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

    @pytest.mark.skip("No matching dataset")
    def test_p4_3s_1f_rgb(self):
        """Test process 4 RGB."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p4_3s_1f_ybr_411(self):
        """Test process 4 YBR with 411 subsampling."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p4_3s_1f_ybr_422(self):
        """Test process 4 YBR with 422 subsampling."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p4_3s_1f_ybr_444(self):
        """Test process 4 YBR with 444 subsampling."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_p4_3s_2f(self):
        """Test process 4 3 sample/px with 2 frames."""
        pass


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLossless(HandlerTestBase):
    """Test the handler with ISO 10918 JPEG images.

    1.2.840.10008.1.2.4.57 : JPEG Lossless, Non-Hierarchical (Process 14)

    Supported Elements
    ------------------
    #Bits Allocated: 8 (for Process 2) or 16 (for Process 4)
    #Bits Stored: 8 (for Process 2) or 12 (for Process 4)
    Samples Per Pixel: 1 or 3
    Number of Frames: N
    Photometric Interpretation: MONOCHROME1, MONOCHROME2, RGB, YBR_FULL,
        YBR_FULL_422
    """
    uid = '1.2.840.10008.1.2.4.57'


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLosslessSV1(HandlerTestBase):
    """Test the handler with ISO 10918 JPEG images.

    1.2.840.10008.1.2.4.70 : JPEG Lossless, Non-Hierarchical, First-Order
    Prediction (Process 14 [Selection Value 1]

    Supported Elements
    ------------------
    #Bits Allocated: 8 (for Process 2) or 16 (for Process 4)
    #Bits Stored: 8 (for Process 2) or 12 (for Process 4)
    Samples Per Pixel: 1 or 3
    Number of Frames: N
    Photometric Interpretation: MONOCHROME1, MONOCHROME2, RGB, YBR_FULL,
        YBR_FULL_422
    """
    uid = '1.2.840.10008.1.2.4.70'

    # Needs reference data
    def test_1s_1f_u_08_08(self):
        """Test process 2 greyscale."""
        ds = self.ds['JPGLosslessP14SV1_1s_1f_8b.dcm']['ds']
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

    @pytest.mark.skip("No matching dataset")
    def test_1s_1f_i_08_08(self):
        """Test process 2 greyscale."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_1s_Nf_u_08_08(self):
        """Test process 2 greyscale."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_1s_1f_u_16_16(self):
        """Test process 2 greyscale."""
        pass

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

    # Needs reference data
    def test_1s_1f_u_16_12(self):
        """Test process 2 greyscale."""
        ds = self.ds['MG1_JPLL']['ds']
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

    # Needs reference data
    def test_1s_1f_u_16_15(self):
        """Test process 2 greyscale."""
        ds = self.ds['RG1_JPLL']['ds']
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

    # Needs reference data
    def test_1s_1f_u_16_10(self):
        """Test process 2 greyscale."""
        ds = self.ds['RG2_JPLL']['ds']
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

    @pytest.mark.skip("No matching dataset")
    def test_1s_Nf_u_16_16(self):
        """Test process 2 greyscale."""
        pass

    def test_3s_1f_u_08_08(self):
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

    @pytest.mark.skip("No matching dataset")
    def test_3s_1f_u_16_16(self):
        """Test process 2 greyscale."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_3s_Nf_u(self):
        """Test process 2 greyscale."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_3s_Nf_u_08_08(self):
        """Test process 2 greyscale."""
        pass

    @pytest.mark.skip("No matching dataset")
    def test_3s_Nf_u_16_16(self):
        """Test process 2 greyscale."""
        pass


# ISO/IEC 14495 JPEG-LS
@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLSLossless(HandlerTestBase):
    """Test the handler with ISO 14495 JPEG-LS images.

    1.2.840.10008.1.2.4.80 : JPEG-LS Lossless Image Compression
    """
    uid = '1.2.840.10008.1.2.4.80'

    # Needs reference data
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

    # Needs reference data
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


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLS(HandlerTestBase):
    """Test the handler with ISO 14495 JPEG-LS images.

    Transfer Syntaxes
    -----------------

    1.2.840.10008.1.2.4.81 : JPEG-LS Lossy (Near-Lossless) Image Compression
    """
    uid = '1.2.840.10008.1.2.4.81'

    # Needs reference data
    def test_1s_1f_i_16_16(self):
        """Test process 2 greyscale."""
        ds = self.ds['CT1_JLSN']['ds']
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

    # Needs reference data
    def test_1s_1f_u_16_12(self):
        """Test process 2 greyscale."""
        ds = self.ds['MG1_JLSN']['ds']
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

    # Needs reference data
    def test_1s_1f_u_16_15(self):
        """Test process 2 greyscale."""
        ds = self.ds['RG1_JLSN']['ds']
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

    # Needs reference data
    def test_1s_1f_u_16_10(self):
        """Test process 2 greyscale."""
        ds = self.ds['RG2_JLSN']['ds']
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

        self.plot(arr)


# ISO/IEC 15444 JPEG 2000 - Expected fail
@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEG2000Lossless(HandlerTestBase):
    """Test the handler with ISO 15444 JPEG2000 images.

    1.2.840.10008.1.2.4.90 : JPEG 2000 Image Compression (Lossless Only)
    """
    uid = '1.2.840.10008.1.2.4.90'

    # Needs to raise exception
    def test_1s_1f_i_16_16(self):
        """Test process 2 greyscale."""
        ds = self.ds['693_J2KR.dcm']['ds']
        libjpeg_handler.SUPPORTED_TRANSFER_SYNTAXES.append(ds.file_meta.TransferSyntaxUID)
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 16 == ds.BitsStored
        assert 1 == ds.PixelRepresentation

        # TODO: should raise an exception
        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'int16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr, cmap='gray')


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEG2000(HandlerTestBase):
    """Test the handler with ISO 15444 JPEG2000 images.

    1.2.840.10008.1.2.4.91 : JPEG 2000 Image Compression
    """
    uid = '1.2.840.10008.1.2.4.91'

    # Needs to raise exception
    def test_1s_1f_i_16_16(self):
        """Test process 2 greyscale."""
        ds = self.ds['693_J2KI.dcm']['ds']
        libjpeg_handler.SUPPORTED_TRANSFER_SYNTAXES.append(ds.file_meta.TransferSyntaxUID)
        assert self.uid == ds.file_meta.TransferSyntaxUID
        assert 1 == ds.SamplesPerPixel
        assert 1 == getattr(ds, 'NumberOfFrames', 1)
        assert 'MONOCHROME' in ds.PhotometricInterpretation
        assert 16 == ds.BitsAllocated
        assert 14 == ds.BitsStored
        assert 1 == ds.PixelRepresentation

        # TODO: should raise an exception
        arr = ds.pixel_array
        assert arr.flags.writeable
        assert 'int16' == arr.dtype
        assert (ds.Rows, ds.Columns) == arr.shape

        #self.plot(arr, cmap='gray')
