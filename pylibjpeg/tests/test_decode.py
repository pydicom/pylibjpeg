"""Tests for standalone decoding."""

from io import BytesIO
import os
from pathlib import Path
import platform
import sys

import pytest

from pylibjpeg import decode
from pylibjpeg.data import JPEG_DIRECTORY
from pylibjpeg.utils import get_decoders


HAS_DECODERS = bool(get_decoders())
RUN_JPEG = bool(get_decoders("JPEG"))
RUN_JPEGLS = bool(get_decoders("JPEG-LS"))
RUN_JPEG2K = bool(get_decoders("JPEG 2000"))


@pytest.mark.skipif(HAS_DECODERS, reason="Decoders available")
class TestNoDecoders(object):
    """Test interactions with no decoders."""
    def test_decode_str(self):
        """Test passing a str to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        assert isinstance(fpath, str)
        with pytest.raises(RuntimeError, match=r"No decoders are available"):
            decode(fpath)

    def test_decode_pathlike(self):
        """Test passing a pathlike to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        p = Path(fpath)
        assert isinstance(p, os.PathLike)
        with pytest.raises(RuntimeError, match=r"No decoders are available"):
            decode(p)

    def test_decode_filelike(self):
        """Test passing a filelike to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        with open(fpath, 'rb') as f:
            msg = r"No decoders are available"
            with pytest.raises(RuntimeError, match=msg):
                decode(f)

    def test_decode_bytes(self):
        """Test passing bytes to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        with open(fpath, 'rb') as f:
            data = f.read()

        assert isinstance(data, bytes)
        msg = r"No decoders are available"
        with pytest.raises(RuntimeError, match=msg):
            decode(data)

    def test_unknown_decoder_type(self):
        """Test unknown decoder type."""
        with pytest.raises(ValueError, match=r"Unknown decoder_type 'TEST'"):
            get_decoders(decoder_type='TEST')


@pytest.mark.skipif(not RUN_JPEG, reason="No JPEG decoders available")
class TestJPEGDecoders(object):
    """Test decoding."""
    def test_decode_str(self):
        """Test passing a str to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        assert isinstance(fpath, str)
        arr = decode(fpath)

    def test_decode_pathlike(self):
        """Test passing a pathlike to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        p = Path(fpath)
        assert isinstance(p, os.PathLike)
        arr = decode(p)

    def test_decode_filelike(self):
        """Test passing a filelike to decode."""
        bs = BytesIO()

        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        with open(fpath, 'rb') as f:
            arr = decode(f)

        with open(fpath, 'rb') as f:
            bs.write(f.read())

        bs.seek(0)
        arr = decode(bs)

    def test_decode_bytes(self):
        """Test passing bytes to decode."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        with open(fpath, 'rb') as f:
            data = f.read()

        assert isinstance(data, bytes)
        arr = decode(data)

    def test_decode_failure(self):
        """Test failure to decode."""
        with pytest.raises(ValueError, match=r"Unable to decode"):
            decode(b'\x00\x00')

    def test_specify_decoder(self):
        """Test specifying the decoder."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        assert isinstance(fpath, str)
        arr = decode(fpath, decoder='libjpeg')

    @pytest.mark.skipif("openjpeg" in get_decoders(), reason="Have openjpeg")
    def test_specify_unknown_decoder(self):
        """Test specifying an unknown decoder."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        assert isinstance(fpath, str)
        with pytest.raises(ValueError, match=r"The 'openjpeg' decoder"):
            decode(fpath, decoder='openjpeg')


@pytest.mark.skipif(not RUN_JPEGLS, reason="No JPEG-LS decoders available")
class TestJPEGLSDecoders(object):
    """Test decoding JPEG-LS files."""
    def setup(self):
        self.basedir = os.path.join(JPEG_DIRECTORY, '14495', 'JLS')

    def test_decode_str(self):
        """Test passing a str to decode."""
        fpath = os.path.join(self.basedir, 'T8C0E0.JLS')
        assert isinstance(fpath, str)
        arr = decode(fpath)

    def test_decode_pathlike(self):
        """Test passing a pathlike to decode."""
        fpath = os.path.join(self.basedir, 'T8C0E0.JLS')
        p = Path(fpath)
        assert isinstance(p, os.PathLike)
        arr = decode(p)

    def test_decode_filelike(self):
        """Test passing a filelike to decode."""
        bs = BytesIO()

        fpath = os.path.join(self.basedir, 'T8C0E0.JLS')
        with open(fpath, 'rb') as f:
            arr = decode(f)

        with open(fpath, 'rb') as f:
            bs.write(f.read())

        bs.seek(0)
        arr = decode(bs)

    def test_decode_bytes(self):
        """Test passing bytes to decode."""
        fpath = os.path.join(self.basedir, 'T8C0E0.JLS')
        with open(fpath, 'rb') as f:
            data = f.read()

        assert isinstance(data, bytes)
        arr = decode(data)

    def test_specify_decoder(self):
        """Test specifying the decoder."""
        fpath = os.path.join(self.basedir, 'T8C0E0.JLS')
        arr = decode(fpath, decoder='libjpeg')

    @pytest.mark.skipif("openjpeg" in get_decoders(), reason="Have openjpeg")
    def test_specify_unknown_decoder(self):
        """Test specifying an unknown decoder."""
        fpath = os.path.join(self.basedir, 'T8C0E0.JLS')
        with pytest.raises(ValueError, match=r"The 'openjpeg' decoder"):
            decode(fpath, decoder='openjpeg')


@pytest.mark.skipif(not RUN_JPEG2K, reason="No JPEG 2000 decoders available")
class TestJPEG2KDecoders(object):
    """Test decoding JPEG 2000 files."""
    def setup(self):
        self.basedir = os.path.join(JPEG_DIRECTORY, '15444', '2KLS')

    def test_decode_str(self):
        """Test passing a str to decode."""
        fpath = os.path.join(self.basedir, '693.j2k')
        assert isinstance(fpath, str)
        arr = decode(fpath)

    def test_decode_pathlike(self):
        """Test passing a pathlike to decode."""
        fpath = os.path.join(self.basedir, '693.j2k')
        p = Path(fpath)
        assert isinstance(p, os.PathLike)
        arr = decode(p)

    def test_decode_filelike(self):
        """Test passing a filelike to decode."""
        bs = BytesIO()

        fpath = os.path.join(self.basedir, '693.j2k')
        with open(fpath, 'rb') as f:
            arr = decode(f)

        with open(fpath, 'rb') as f:
            bs.write(f.read())

        bs.seek(0)
        arr = decode(bs)

    def test_decode_bytes(self):
        """Test passing bytes to decode."""
        fpath = os.path.join(self.basedir, '693.j2k')
        with open(fpath, 'rb') as f:
            data = f.read()

        assert isinstance(data, bytes)
        arr = decode(data)

    def test_specify_decoder(self):
        """Test specifying the decoder."""
        fpath = os.path.join(self.basedir, '693.j2k')
        arr = decode(fpath, decoder='openjpeg')

    @pytest.mark.skipif("libjpeg" in get_decoders(), reason="Have libjpeg")
    def test_specify_unknown_decoder(self):
        """Test specifying an unknown decoder."""
        fpath = os.path.join(self.basedir, '693.j2k')
        with pytest.raises(ValueError, match=r"The 'libjpeg' decoder"):
            decode(fpath, decoder='libjpeg')
