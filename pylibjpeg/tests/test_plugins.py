"""Tests for the plugins"""

import os
import platform
import sys

import pytest

from pylibjpeg.plugins import get_plugins, get_decoders, get_encoders
from pylibjpeg.pydicom.utils import (
    decoder_from_uid, encoder_from_uid, get_decodable_uids,
    get_dicom_decoders, get_dicom_encoders, get_encodable_uids,
    get_uid_decoder_dict, get_uid_encoder_dict
)

# TODO: Switch this over to openjpeg plugin
try:
    import libjpeg
    HAS_LIBJPEG = True
except ImportError:
    HAS_LIBJPEG = False


HAS_PLUGINS = get_plugins() != []


@pytest.mark.skipif(HAS_PLUGINS, reason="Plugins available")
class TestNoPlugins(object):
    """Tests for plugins without any available."""
    def test_get_plugins(self):
        """Test get_plugins()."""
        assert [] == get_plugins()

    def test_get_decoders(self):
        """Test get_decoders()."""
        assert {} == get_decoders()

    def test_get_encoders(self):
        """Test get_encoders()."""
        assert {} == get_encoders()

    def test_decoder_from_uid(self):
        """Test decoder_from_uid()."""
        msg = (
            r"No decoder is available for the Transfer Syntax UID - '1.2.3.4'"
        )
        with pytest.raises(NotImplementedError, match=msg):
            decoder_from_uid('1.2.3.4')

    def test_encoder_from_uid(self):
        """Test encoder_from_uid()."""
        msg = (
            r"No encoder is available for the Transfer Syntax UID - '1.2.3.4'"
        )
        with pytest.raises(NotImplementedError, match=msg):
            encoder_from_uid('1.2.3.4')

    def test_get_decodable_uids(self):
        """Test get_decodable_uids()."""
        assert [] == get_decodable_uids()

    def test_get_encodable_uids(self):
        """Test get_encodable_uids()."""
        assert [] == get_encodable_uids()

    def test_get_dicom_decoders(self):
        """Test get_dicom_decoders()."""
        assert {} == get_dicom_decoders()

    def test_get_dicom_encoders(self):
        """Test get_dicom_encoders()."""
        assert {} == get_dicom_encoders()

    def test_get_uid_decoder_dict(self):
        """Test get_uid_decoder_dict()."""
        assert {} == get_uid_decoder_dict()

    def test_get_uid_encoder_dict(self):
        """Test get_uid_encoder_dict()."""
        assert {} == get_uid_encoder_dict()


@pytest.mark.skipif(not HAS_PLUGINS or not HAS_LIBJPEG, reason="No libjpeg")
class TestPlugins(object):
    """Tests for plugins with a plugin available."""
    def test_get_plugins(self):
        """Test get_plugins()."""
        assert ['libjpeg'] == get_plugins()

    def test_get_decoders(self):
        """Test get_decoders()."""
        assert 'libjpeg' in get_decoders()

    @pytest.mark.skip()
    def test_get_decoders_none(self):
        """Test get_decoders() with no decoders."""
        assert {} == get_decoders()

    @pytest.mark.skip()
    def test_get_decoders(self):
        """Test get_decoders()."""
        assert 'libjpeg' in get_encoders()

    def test_get_encoders_none(self):
        """Test get_encoders()."""
        assert {} == get_encoders()

    def test_decoder_from_uid(self):
        """Test decoder_from_uid()."""
        func = decoder_from_uid('1.2.840.10008.1.2.4.50')
        assert func is not None

    @pytest.mark.skip()
    def test_encoder_from_uid(self):
        """Test encoder_from_uid()."""
        msg = (
            r"No encoder is available for the Transfer Syntax UID - '1.2.3.4'"
        )
        with pytest.raises(NotImplementedError, match=msg):
            encoder_from_uid('1.2.3.4')

    def test_get_dicom_decoders(self):
        """Test get_dicom_decoders() with only a decoder plugin."""
        dec = get_dicom_decoders()
        assert 'libjpeg' in dec
        assert '1.2.840.10008.1.2.4.50' in dec['libjpeg']

    @pytest.mark.skip()
    def test_get_dicom_decoders_none(self):
        """Test get_dicom_decoders() with only a decoder plugin."""
        dec = get_dicom_decoders()
        assert 'libjpeg' in dec
        assert {} == dec['libjpeg']

    @pytest.mark.skip()
    def test_get_dicom_encoders(self):
        """Test get_dicom_encoders() with only a decoder plugin."""
        enc = get_dicom_encoders()
        assert 'libjpeg' in enc
        assert '1.2.840.10008.1.2.4.50' in enc['libjpeg']

    def test_get_dicom_encoders_none(self):
        """Test get_dicom_encoders() with only a decoder plugin."""
        enc = get_dicom_encoders()
        assert 'libjpeg' in enc
        assert {} == enc['libjpeg']

    def test_get_decodable_uids(self):
        """Test get_decodable_uids()."""
        reference = [
            '1.2.840.10008.1.2.4.50',
            '1.2.840.10008.1.2.4.51',
            '1.2.840.10008.1.2.4.57',
            '1.2.840.10008.1.2.4.70',
            '1.2.840.10008.1.2.4.80',
            '1.2.840.10008.1.2.4.81',
        ]
        syntaxes = get_decodable_uids()
        for uid in syntaxes:
            assert uid in reference

    @pytest.mark.skip()
    def test_get_encodable_uids(self):
        """Test get_encodable_uids()."""
        reference = []
        syntaxes = get_encodable_uids()
        for uid in syntaxes:
            assert uid in reference

    def test_get_uid_decoder_dict(self):
        """Test get_uid_decoder_dict()."""
        reference = [
            '1.2.840.10008.1.2.4.50',
            '1.2.840.10008.1.2.4.51',
            '1.2.840.10008.1.2.4.57',
            '1.2.840.10008.1.2.4.70',
            '1.2.840.10008.1.2.4.80',
            '1.2.840.10008.1.2.4.81',
        ]
        decoders = get_uid_decoder_dict()
        for uid in reference:
            assert uid in decoders

    @pytest.mark.skip()
    def test_get_uid_encoder_dict(self):
        """Test get_uid_encoder_dict()."""
        reference = []
        encoders = get_uid_encoder_dict()
        for uid in reference:
            assert uid in encoders
