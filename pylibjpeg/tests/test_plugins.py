"""Tests for the plugins"""

import os
import platform
import sys

import pytest

from pylibjpeg.plugins import (
    get_plugin_coders, get_plugins, get_transfer_syntaxes, get_decoder,
    get_encoder, get_decoders
)

# TODO: Switch this over to openjpeg
try:
    import libjpeg
    HAS_LIBJPEG = True
except ImportError:
    HAS_LIBJPEG = False

HAS_PLUGINS = get_plugins() != []


@pytest.mark.skipif(HAS_PLUGINS, reason="Plugins available")
class TestNoPlugins(object):
    """Tests for plugins without any available."""
    def test_check_plugins(self):
        """Test check_plugins()."""
        dec, enc = get_plugin_coders()
        assert {} == dec
        assert {} == enc

    def test_get_plugins(self):
        """Test get_plugins()."""
        assert [] == get_plugins()

    def test_get_transfer_syntaxes(self):
        """Test get_plugins()."""
        msg = r"Either 'decodable' or 'encodable' must be True"
        with pytest.raises(ValueError, match=msg):
            get_transfer_syntaxes()

        assert [] == get_transfer_syntaxes(decodable=True)
        assert [] == get_transfer_syntaxes(encodable=True)

    def test_get_decoder_raises(self):
        """Test get_decoder()."""
        msg = r"No decoder is available for the Transfer Syntax UID - '1.2.3'"
        with pytest.raises(NotImplementedError, match=msg):
            get_decoder('1.2.3')

    def test_get_encoder_raises(self):
        """Test get_encoder()."""
        msg = r"No encoder is available for the Transfer Syntax UID - '1.2.3'"
        with pytest.raises(NotImplementedError, match=msg):
            get_encoder('1.2.3')

    def test_get_decoders(self):
        """Test get_decoders()."""
        assert {} == get_decoders()


@pytest.mark.skipif(not HAS_PLUGINS or not HAS_LIBJPEG, reason="No libjpeg")
class TestPlugins(object):
    """Tests for plugins with a plugin available."""
    def test_check_plugins(self):
        """Test check_plugins()."""
        dec, enc = get_plugin_coders()
        assert {} != dec
        assert {} != enc

    def test_check_plugins_dec_only(self):
        """Test check_plugins() with only a decoder plugin."""
        dec, enc = get_plugin_coders()
        assert 'libjpeg' in enc
        assert {} == enc['libjpeg']
        assert 'libjpeg' in dec
        assert '1.2.840.10008.1.2.4.50' in dec['libjpeg']

    def test_get_transfer_syntaxes(self):
        """Test get_plugins()."""
        msg = r"Either 'decodable' or 'encodable' must be True"
        with pytest.raises(ValueError, match=msg):
            get_transfer_syntaxes()

        reference = [
            '1.2.840.10008.1.2.4.50',
            '1.2.840.10008.1.2.4.51',
            '1.2.840.10008.1.2.4.57',
            '1.2.840.10008.1.2.4.70',
            '1.2.840.10008.1.2.4.80',
            '1.2.840.10008.1.2.4.81',
        ]
        syntaxes = get_transfer_syntaxes(decodable=True)
        for uid in syntaxes:
            assert uid in reference

        assert [] == get_transfer_syntaxes(encodable=True)

    def test_get_decoder(self):
        """Test get_decoder()."""
        decoder = get_decoder('1.2.840.10008.1.2.4.50')

    def test_get_decoders(self):
        """Test get_decoders()."""
        reference = [
            '1.2.840.10008.1.2.4.50',
            '1.2.840.10008.1.2.4.51',
            '1.2.840.10008.1.2.4.57',
            '1.2.840.10008.1.2.4.70',
            '1.2.840.10008.1.2.4.80',
            '1.2.840.10008.1.2.4.81',
        ]
        decoders = get_decoders()
        for uid in reference:
            assert uid in decoders
