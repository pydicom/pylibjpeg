"""Tests for the pylibjpeg pixel data handler."""

from io import BytesIO
import os
import tempfile
from tempfile import NamedTemporaryFile
import pytest

from pylibjpeg.libjpeg import reconstruct

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(TEST_DIR, '../data')
DIR_10918 = os.path.join(DATA_DIR, 'jpg', '10918')
DIR_14495 = os.path.join(DATA_DIR, 'jpg', '14495')


def test_reconstruct_no_alpha():
    """Basic test of reconstruct()."""
    # Windows workarounds
    tempdir = tempfile.TemporaryDirectory()
    inname = os.path.join(tempdir.name, os.urandom(24).hex())
    outname = os.path.join(tempdir.name, os.urandom(24).hex())

    infile = open(inname, 'wb')
    with open(os.path.join(DIR_14495, 'JLS', 'T8C0E0.JLS'), 'rb') as fp:
        infile.write(fp.read())

    infile.close()

    # Output file
    reconstruct(
        inname, outname, colourspace=0, falpha=None, upsample=True
    )
    with open(outname, 'rb') as f:
        data = f.read()

    tempdir.cleanup()

    assert b'P6\n256 256' == data[:10]


@pytest.mark.skip("Needs more understanding")
def test_reconstruct_alpha():
    """Basic test of reconstruct() with pretend alpha data."""
    # Input file
    infile = NamedTemporaryFile('rb+')
    with open(os.path.join(DIR_10918, 'p1', 'A1.JPG'), 'rb') as fp:
        infile.write(fp.read())

    # Output file - CMY
    outfile = NamedTemporaryFile('rb+')
    # Output file - "alpha"
    alphafile = NamedTemporaryFile('rb+')

    reconstruct(
        infile.name, outfile.name, colourspace=0,
        falpha=alphafile.name, upsample=True
    )

    assert b'' == alphafile.read(10)
    assert b'P6\n256 256' == outfile.read(10)
