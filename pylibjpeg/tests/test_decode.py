"""Tests for standalone decoding."""

from io import BytesIO
import os
from pathlib import Path
import platform
import sys

import pytest

from pylibjpeg import decode
from pylibjpeg.plugins import get_plugins
from pylibjpeg.data import JPEG_DIRECTORY

HAS_PLUGINS = get_plugins() != []


@pytest.mark.skipif(HAS_PLUGINS, reason="Plugins available")
class TestNoPlugins(object):
    """Test interactions with no plugins."""
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


@pytest.mark.skipif(not HAS_PLUGINS, reason="Plugins unavailable")
class TestPlugins(object):
    """Test decoding with plugins."""
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

    def test_specify_unknown_decoder(self):
        """Test specifying an unknown decoder."""
        fpath = os.path.join(JPEG_DIRECTORY, '10918', 'p1', 'A1.JPG')
        assert isinstance(fpath, str)
        with pytest.raises(ValueError, match=r"The 'openjpeg' decoder"):
            decode(fpath, decoder='openjpeg')
