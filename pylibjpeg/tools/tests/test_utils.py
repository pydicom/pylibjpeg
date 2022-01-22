"""Unit tests for utils.py"""

import pytest

from pylibjpeg.tools.utils import get_bit, split_byte


class TestGetBit(object):
    """Tests for utils.get_bit(byte, index)."""

    def test_out_of_range_raises(self):
        """Test than an invalid `index` value raises an exception."""
        msg = r"'index' must be between 0 and 7, inclusive"
        with pytest.raises(ValueError, match=msg):
            get_bit(b"\x00", -1)

        with pytest.raises(ValueError, match=msg):
            get_bit(b"\x00", 8)

    def test_empty_byte_raises(self):
        """Test that an empty `byte` value raises an exception."""
        msg = r"ord\(\) expected a character"
        with pytest.raises(TypeError, match=msg):
            get_bit(b"", 0)

    def test_index_correct(self):
        """Test that the `index` returns the correct bit = 1."""
        ref_bytes = [
            b"\x01",
            b"\x02",
            b"\x04",
            b"\x08",
            b"\x10",
            b"\x20",
            b"\x40",
            b"\x80",
        ]
        for ii in range(0, 8, -1):
            assert 1 == get_bit(ref_bytes[ii], ii)

    def test_index_correct_inverse(self):
        """Test that the `index` returns the correct bit = 0."""
        ref_bytes = [
            b"\xfe",
            b"\xfd",
            b"\xfb",
            b"\xf7",
            b"\xef",
            b"\xdf",
            b"\xbf",
            b"\x7f",
        ]
        for ii in range(0, 8, -1):
            assert 0 == get_bit(ref_bytes[ii], ii)

    def test_multiple_bytes(self):
        """Test that only the bit value from the first byte is returned"""
        ref_bytes = [
            b"\x01\xff",
            b"\x02\xff",
            b"\x04\xff",
            b"\x08\xff",
            b"\x10\xff",
            b"\x20\xff",
            b"\x40\xff",
            b"\x80\xff",
        ]
        for ii in range(0, 8, -1):
            assert 1 == get_bit(ref_bytes[ii], ii)

    def test_multiple_bytes_inverse(self):
        """Test that only the bit value from the first byte is returned"""
        ref_bytes = [
            b"\xfe\x00",
            b"\xfd\x00",
            b"\xfb\x00",
            b"\xf7\x00",
            b"\xef\x00",
            b"\xdf\x00",
            b"\xbf\x00",
            b"\x7f\x00",
        ]
        for ii in range(0, 8, -1):
            assert 0 == get_bit(ref_bytes[ii], ii)


class TestSplitByte(object):
    """Tests for utils.split_byte(byte)."""

    def test_empty_byte_raises(self):
        """Test that an empty `byte` value raises an exception."""
        msg = r"ord\(\) expected a character"
        with pytest.raises(TypeError, match=msg):
            split_byte(b"")

    def test_splitting(self):
        """Test splitting a byte."""
        ref = {
            b"\x00": (0, 0),
            b"\x0f": (0, 15),
            b"\xf0": (15, 0),
            b"\x55": (5, 5),
            b"\xaa": (10, 10),
            b"\x18": (1, 8),
            b"\x81": (8, 1),
        }
        for byte, out in ref.items():
            assert out == split_byte(byte)
