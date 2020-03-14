"""Tests for the TravisCI testing environments"""

import logging
import os
import platform
import sys

import pytest

from pylibjpeg import debug_logger


def test_debug_logger(caplog):
    """Test the debug logger works."""
    debug_logger()
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.DEBUG):
        logger.debug("This is a test")

    assert 'This is a test' in caplog.text

    # Reset
    logging.getLogger('pylibjpeg').handlers = []


def get_envar(envar):
    """Return the value of the environmental variable `envar`.

    Parameters
    ----------
    envar : str
        The environmental variable to check for.

    Returns
    -------
    str or None
        If the envar is present then return its value otherwise returns None.
    """
    if envar in os.environ:
        return os.environ.get(envar)

    return None


IN_TRAVIS = get_envar("TRAVIS") == 'true'


@pytest.mark.skipif(not IN_TRAVIS, reason="Tests not running in Travis")
class TestBuilds(object):
    """Tests for the testing builds in Travis CI."""
    def test_os(self):
        """Test that the OS is correct."""
        os_name = get_envar('TRAVIS_OS_NAME')
        if not os_name:
            raise RuntimeError("No 'TRAVIS_OS_NAME' envar has been set")

        if os_name == 'osx':
            assert platform.system() == 'Darwin'
        elif os_name == 'linux':
            assert platform.system() == 'Linux'
            assert "CPython" in platform.python_implementation()
        elif os_name == 'windows':
            assert platform.system() == 'Windows'
        else:
            raise NotImplementedError("Unknown 'TRAVIS_OS_NAME' value")

    def test_python_version(self):
        """Test that the python version is correct."""
        version = get_envar('TRAVIS_PYTHON_VERSION')
        if not version:
            raise RuntimeError("No 'TRAVIS_PYTHON_VERSION' envar has been set")

        version = tuple([int(vv) for vv in version.split('.')])
        assert version[:2] == sys.version_info[:2]
