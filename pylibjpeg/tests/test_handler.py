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


from pylibjpeg import add_handler, remove_handler
from pylibjpeg import libjpeg_handler


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


class HandlerBase(object):
    """Baseclass for handler tests."""
    def setup(self):
        add_handler()

    def teardown(self):
        remove_handler()


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGBaseline(HandlerBase):
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
    def test_1s_1f(self):
        """Test greyscale."""
        pass

    def test_1s_2f(self):
        """Test greyscale with 2 frames."""
        pass

    def test_3s_1f_rgb(self):
        """Test RGB."""
        pass

    def test_3s_1f_ybr_411(self):
        """Test YBR with 411 subsampling."""
        pass

    def test_3s_1f_ybr_422(self):
        """Test YBR with 422 subsampling."""
        pass

    def test_3s_1f_ybr_444(self):
        """Test YBR with 444 subsampling."""
        pass

    def test_3s_2f(self):
        """Test 3 sample/px with 2 frames."""
        pass


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGExtended(HandlerBase):
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
    def test_p2_1s_1f(self):
        """Test process 2 greyscale."""
        pass

    def test_p2_1s_2f(self):
        """Test process 2 greyscale with 2 frames."""
        pass

    def test_p2_3s_1f_rgb(self):
        """Test process 2 RGB."""
        pass

    def test_p2_3s_1f_ybr_411(self):
        """Test process 2 YBR with 411 subsampling."""
        pass

    def test_p2_3s_1f_ybr_422(self):
        """Test process 2 YBR with 422 subsampling."""
        pass

    def test_p2_3s_1f_ybr_444(self):
        """Test process 2 YBR with 444 subsampling."""
        pass

    def test_p2_3s_2f(self):
        """Test process 2 3 sample/px with 2 frames."""
        pass

    def test_p4_1s_1f(self):
        """Test process 4 greyscale."""
        pass

    def test_p4_1s_2f(self):
        """Test process 4 greyscale with 2 frames."""
        pass

    def test_p4_3s_1f_rgb(self):
        """Test process 4 RGB."""
        pass

    def test_p4_3s_1f_ybr_411(self):
        """Test process 4 YBR with 411 subsampling."""
        pass

    def test_p4_3s_1f_ybr_422(self):
        """Test process 4 YBR with 422 subsampling."""
        pass

    def test_p4_3s_1f_ybr_444(self):
        """Test process 4 YBR with 444 subsampling."""
        pass

    def test_p4_3s_2f(self):
        """Test process 4 3 sample/px with 2 frames."""
        pass


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLossless(HandlerBase):
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
    pass

@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLosslessSV1(HandlerBase):
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
    pass


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLSLossless(HandlerBase):
    """Test the handler with ISO 14495 JPEG-LS images.

    1.2.840.10008.1.2.4.80 : JPEG-LS Lossless Image Compression
    """
    pass


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEGLS(HandlerBase):
    """Test the handler with ISO 14495 JPEG-LS images.

    Transfer Syntaxes
    -----------------

    1.2.840.10008.1.2.4.81 : JPEG-LS Lossy (Near-Lossless) Image Compression
    """
    pass


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEG2000Lossless(HandlerBase):
    """Test the handler with ISO 15444 JPEG2000 images.

    1.2.840.10008.1.2.4.90 : JPEG 2000 Image Compression (Lossless Only)
    """
    pass


@pytest.mark.skipif(not HAS_NP or not HAS_PYDICOM, reason="No dependencies")
class TestJPEG2000(HandlerBase):
    """Test the handler with ISO 15444 JPEG2000 images.

    1.2.840.10008.1.2.4.91 : JPEG 2000 Image Compression
    """
    pass
