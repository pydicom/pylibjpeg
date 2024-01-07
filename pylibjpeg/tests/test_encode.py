"""Tests for standalone encoding."""

import pytest

from pylibjpeg.utils import get_encoders, _encode, get_pixel_data_encoders


HAS_ENCODERS = bool(get_encoders())
HAS_PIXEL_DATA_ENCODERS = bool(get_pixel_data_encoders())


@pytest.mark.skipif(HAS_ENCODERS, reason="Encoders available")
class TestNoEncoders:
    """Test interactions with no encoders."""

    def test_encode_raises(self):
        """Test encode raises if no encoders available."""
        with pytest.raises(RuntimeError, match=r"No encoders are available"):
            _encode(None)

    def test_get_encoders(self):
        """Tests for get_encoders()"""
        assert get_encoders() == {}

        msg = "No matching plugin entry point for 'foo'"
        with pytest.raises(KeyError, match=msg):
            get_encoders("foo")


@pytest.mark.skipif(not HAS_PIXEL_DATA_ENCODERS, reason="No encoders available")
class TestEncoders:
    """Test get_pixel_data_encoders()"""

    def test_v1_get_pixel_data_encoders(self):
        """Test version 1 of get_pixel_data_encoders()"""
        encoders = get_pixel_data_encoders(version=1)
        assert encoders != {}
        for encoder in encoders:
            assert callable(encoders[encoder])

    def test_v2_get_pixel_data_encoders(self):
        """Test version 2 of get_pixel_data_encoders()"""
        encoders = get_pixel_data_encoders(version=2)
        assert encoders != {}
        for encoder in encoders:
            for plugin in encoders[encoder]:
                assert callable(encoders[encoder][plugin])
