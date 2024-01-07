"""Tests for standalone decoding."""

from io import BytesIO
import logging
import os
from pathlib import Path

import pytest

from pylibjpeg import decode
from pylibjpeg.data import JPEG_DIRECTORY
from pylibjpeg.utils import get_decoders, get_pixel_data_decoders


HAS_DECODERS = bool(get_decoders()) or bool(get_pixel_data_decoders())
RUN_JPEG = bool(get_decoders("JPEG"))
RUN_JPEGLS = bool(get_decoders("JPEG-LS"))
RUN_JPEG2K = bool(get_decoders("JPEG 2000"))


@pytest.mark.skipif(HAS_DECODERS, reason="Decoders available")
class TestNoDecoders:
    """Test interactions with no decoders."""

    def test_decode_str(self):
        """Test passing a str to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        assert isinstance(fpath, str)
        with pytest.raises(RuntimeError, match=r"No JPEG decoders are available"):
            decode(fpath)

    def test_decode_pathlike(self):
        """Test passing a pathlike to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        p = Path(fpath)
        assert isinstance(p, os.PathLike)
        with pytest.raises(RuntimeError, match=r"No JPEG decoders are available"):
            decode(p)

    def test_decode_filelike(self):
        """Test passing a filelike to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        with open(fpath, "rb") as f:
            msg = r"No JPEG decoders are available"
            with pytest.raises(RuntimeError, match=msg):
                decode(f)

    def test_decode_bytes(self):
        """Test passing bytes to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        with open(fpath, "rb") as f:
            data = f.read()

        assert isinstance(data, bytes)
        msg = r"No JPEG decoders are available"
        with pytest.raises(RuntimeError, match=msg):
            decode(data)

    def test_unknown_decoder_type(self):
        """Test unknown decoder type."""
        msg = "No matching plugin entry point for 'foo'"
        with pytest.raises(KeyError, match=msg):
            get_decoders(decoder_type="foo")

    def test_get_decoders(self, caplog):
        """Tests for get_decoders()"""
        with caplog.at_level(logging.DEBUG, logger="pylibjpeg"):
            get_decoders()
            assert (
                "No plugins found for entry point 'pylibjpeg.jpeg_decoders'"
            ) in caplog.text

        caplog.clear()
        with caplog.at_level(logging.DEBUG, logger="pylibjpeg"):
            assert get_decoders("JPEG-LS") == {}
            assert (
                "No plugins found for entry point 'pylibjpeg.jpeg_ls_decoders'"
            ) in caplog.text

    def test_get_decoders_raises(self):
        """Test exception raised if invalid decoder type."""
        msg = "No matching plugin entry point for 'JPEG XX'"
        with pytest.raises(KeyError, match=msg):
            get_decoders("JPEG XX")

    def test_get_pixel_data_decoders(self, caplog):
        """Tests for get_pixel_data_decoders()"""
        with caplog.at_level(logging.DEBUG, logger="pylibjpeg"):
            get_pixel_data_decoders()
            assert (
                "No plugins found for entry point 'pylibjpeg.pixel_data_decoders'"
            ) in caplog.text

        caplog.clear()
        with caplog.at_level(logging.DEBUG, logger="pylibjpeg"):
            get_pixel_data_decoders(version=2)
            assert (
                "No plugins found for entry point 'pylibjpeg.pixel_data_decoders'"
            ) in caplog.text


@pytest.mark.skipif(not RUN_JPEG, reason="No JPEG decoders available")
class TestJPEGDecoders:
    """Test decoding."""

    def test_decode_str(self):
        """Test passing a str to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        assert isinstance(fpath, str)
        decode(fpath)

    def test_decode_pathlike(self):
        """Test passing a pathlike to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        p = Path(fpath)
        assert isinstance(p, os.PathLike)
        decode(p)

    def test_decode_filelike(self):
        """Test passing a filelike to decode."""
        bs = BytesIO()

        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        with open(fpath, "rb") as f:
            decode(f)

        with open(fpath, "rb") as f:
            bs.write(f.read())

        bs.seek(0)
        decode(bs)

    def test_decode_bytes(self):
        """Test passing bytes to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        with open(fpath, "rb") as f:
            data = f.read()

        assert isinstance(data, bytes)
        decode(data)

    def test_decode_failure(self):
        """Test failure to decode."""
        with pytest.raises(ValueError, match=r"Unable to decode"):
            decode(b"\x00\x00")

    def test_specify_decoder(self):
        """Test specifying the decoder."""
        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        assert isinstance(fpath, str)
        decode(fpath, decoder="libjpeg")

    @pytest.mark.skipif("openjpeg" in get_decoders(), reason="Have openjpeg")
    def test_specify_unknown_decoder(self):
        """Test specifying an unknown decoder."""
        fpath = os.path.join(JPEG_DIRECTORY, "10918", "p1", "A1.JPG")
        assert isinstance(fpath, str)
        with pytest.raises(ValueError, match=r"The 'openjpeg' decoder"):
            decode(fpath, decoder="openjpeg")


@pytest.mark.skipif(not RUN_JPEGLS, reason="No JPEG-LS decoders available")
class TestJPEGLSDecoders:
    """Test decoding JPEG-LS files."""

    def setup_method(self):
        self.basedir = os.path.join(JPEG_DIRECTORY, "14495", "JLS")

    def test_decode_str(self):
        """Test passing a str to decode."""
        fpath = os.path.join(self.basedir, "T8C0E0.JLS")
        assert isinstance(fpath, str)
        decode(fpath)

    def test_decode_pathlike(self):
        """Test passing a pathlike to decode."""
        fpath = os.path.join(self.basedir, "T8C0E0.JLS")
        p = Path(fpath)
        assert isinstance(p, os.PathLike)
        decode(p)

    def test_decode_filelike(self):
        """Test passing a filelike to decode."""
        bs = BytesIO()

        fpath = os.path.join(self.basedir, "T8C0E0.JLS")
        with open(fpath, "rb") as f:
            decode(f)

        with open(fpath, "rb") as f:
            bs.write(f.read())

        bs.seek(0)
        decode(bs)

    def test_decode_bytes(self):
        """Test passing bytes to decode."""
        fpath = os.path.join(self.basedir, "T8C0E0.JLS")
        with open(fpath, "rb") as f:
            data = f.read()

        assert isinstance(data, bytes)
        decode(data)

    def test_specify_decoder(self):
        """Test specifying the decoder."""
        fpath = os.path.join(self.basedir, "T8C0E0.JLS")
        decode(fpath, decoder="libjpeg")

    @pytest.mark.skipif("openjpeg" in get_decoders(), reason="Have openjpeg")
    def test_specify_unknown_decoder(self):
        """Test specifying an unknown decoder."""
        fpath = os.path.join(self.basedir, "T8C0E0.JLS")
        with pytest.raises(ValueError, match=r"The 'openjpeg' decoder"):
            decode(fpath, decoder="openjpeg")


@pytest.mark.skipif(not RUN_JPEG2K, reason="No JPEG 2000 decoders available")
class TestJPEG2KDecoders:
    """Test decoding JPEG 2000 files."""

    def setup_method(self):
        self.basedir = os.path.join(JPEG_DIRECTORY, "15444", "2KLS")

    def test_decode_str(self):
        """Test passing a str to decode."""
        fpath = os.path.join(self.basedir, "693.j2k")
        assert isinstance(fpath, str)
        decode(fpath)

    def test_decode_pathlike(self, caplog):
        """Test passing a pathlike to decode."""
        fpath = os.path.join(self.basedir, "693.j2k")
        p = Path(fpath)
        assert isinstance(p, os.PathLike)
        with caplog.at_level(logging.DEBUG, logger="pylibjpeg"):
            decode(p)
            assert (
                "Found plugin(s) 'openjpeg' for entry point "
                "'pylibjpeg.jpeg_2000_decoders'"
            ) in caplog.text

    def test_decode_filelike(self):
        """Test passing a filelike to decode."""
        bs = BytesIO()

        fpath = os.path.join(self.basedir, "693.j2k")
        with open(fpath, "rb") as f:
            decode(f)

        with open(fpath, "rb") as f:
            bs.write(f.read())

        bs.seek(0)
        decode(bs)

    def test_decode_bytes(self):
        """Test passing bytes to decode."""
        fpath = os.path.join(self.basedir, "693.j2k")
        with open(fpath, "rb") as f:
            data = f.read()

        assert isinstance(data, bytes)
        decode(data)

    def test_specify_decoder(self):
        """Test specifying the decoder."""
        fpath = os.path.join(self.basedir, "693.j2k")
        decode(fpath, decoder="openjpeg")

    @pytest.mark.skipif(RUN_JPEGLS, reason="Have libjpeg")
    def test_specify_unknown_decoder(self):
        """Test specifying an unknown decoder."""
        fpath = os.path.join(self.basedir, "693.j2k")
        with pytest.raises(ValueError, match=r"The 'libjpeg' decoder"):
            decode(fpath, decoder="libjpeg")

    def test_v1_get_pixel_data_decoders(self, caplog):
        """Test version 1 of get_pixel_data_decoders()"""
        with caplog.at_level(logging.DEBUG, logger="pylibjpeg"):
            decoders = get_pixel_data_decoders()

            assert "1.2.840.10008.1.2.4.90" in decoders
            assert callable(decoders["1.2.840.10008.1.2.4.90"])
            assert (
                "Found plugin(s) for entry point 'pylibjpeg.pixel_data_decoders'"
            ) in caplog.text
            assert (
                "Found plugin 'openjpeg' for UID '1.2.840.10008.1.2.4.90'"
            ) in caplog.text

    def test_v2_get_pixel_data_decoders(self, caplog):
        """Test version 2 of get_pixel_data_decoders()"""
        with caplog.at_level(logging.DEBUG, logger="pylibjpeg"):
            decoders = get_pixel_data_decoders(version=2)
            assert "1.2.840.10008.1.2.4.90" in decoders
            assert "openjpeg" in decoders["1.2.840.10008.1.2.4.90"]
            for plugin in decoders["1.2.840.10008.1.2.4.90"]:
                assert callable(decoders["1.2.840.10008.1.2.4.90"][plugin])
                assert (
                    f"Found plugin '{plugin}' for UID '1.2.840.10008.1.2.4.90'"
                ) in caplog.text

            assert (
                "Found plugin(s) for entry point 'pylibjpeg.pixel_data_decoders'"
            ) in caplog.text
