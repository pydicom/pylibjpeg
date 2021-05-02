
import logging
import os
from pkg_resources import iter_entry_points
from struct import unpack

import numpy as np


LOGGER = logging.getLogger(__name__)


def decode(data, decoder=None, kwargs=None):
    """Return the decoded JPEG image as a :class:`numpy.ndarray`.

    Parameters
    ----------
    data : str, file-like, os.PathLike, or bytes
        The data to decode. May be a path to a file (as ``str`` or
        path-like), a file-like, or a ``bytes`` containing the encoded binary
        data.
    decoder : callable, optional
        The plugin to use when decoding the data. If not used then all
        available decoders will be tried.
    kwargs : dict
        A ``dict`` containing keyword parameters to pass to the decoder.

    Returns
    -------
    numpy.ndarray
        An ``ndarray`` containing the decoded image data.

    Raises
    ------
    RuntimeError
        If `decoder` is not ``None`` and the corresponding plugin is not
        available.
    """
    decoders = get_decoders()
    if not decoders:
        raise RuntimeError("No decoders are available")

    if isinstance(data, (str, os.PathLike)):
        with open(str(data), 'rb') as f:
            data = f.read()
    elif isinstance(data, bytes):
        pass
    else:
        # Try file-like
        data = data.read()

    kwargs = kwargs or {}

    if decoder is not None:
        try:
            return decoders[decoder](data, **kwargs)
        except KeyError:
            raise ValueError(f"The '{decoder}' decoder is not available")

    for name, decoder in decoders.items():
        try:
            return decoder(data, **kwargs)
        except Exception as exc:
            LOGGER.debug(f"Decoding with {name} plugin failed")
            LOGGER.exception(exc)

    # If we made it here then we were unable to decode the data
    raise ValueError("Unable to decode the data")


def get_decoders(decoder_type=None):
    """Return a :class:`dict` of JPEG decoders as {package: callable}.

    Parameters
    ----------
    decoder_type : str, optional
        The class of decoders to return, one of:

        * ``"JPEG"`` - ISO/IEC 10918 JPEG decoders
        * ``"JPEG XT"`` - ISO/IEC 18477 JPEG decoders
        * ``"JPEG-LS"`` - ISO/IEC 14495 JPEG decoders
        * ``"JPEG 2000"`` - ISO/IEC 15444 JPEG decoders
        * ``"JPEG XS"`` - ISO/IEC 21122 JPEG decoders
        * ``"JPEG XL"`` - ISO/IEC 18181 JPEG decoders

        If no `decoder_type` is used then all available decoders will be
        returned.

    Returns
    -------
    dict
        A dict of ``{'package_name': <decoder function>}``.
    """
    entry_points = {
        "JPEG" : "pylibjpeg.jpeg_decoders",
        "JPEG XT" : "pylibjpeg.jpeg_xt_decoders",
        "JPEG-LS" : "pylibjpeg.jpeg_ls_decoders",
        "JPEG 2000" : "pylibjpeg.jpeg_2000_decoders",
        "JPEG XR" : "pylibjpeg.jpeg_xr_decoders",
        "JPEG XS" : "pylibjpeg.jpeg_xs_decoders",
        "JPEG XL" : "pylibjpeg.jpeg_xl_decoders",
    }
    if decoder_type is None:
        decoders = {}
        for entry_point in entry_points.values():
            decoders.update({
                val.name: val.load() for val in iter_entry_points(entry_point)
            })
        return decoders

    try:
        return {
            val.name: val.load()
            for val in iter_entry_points(entry_points[decoder_type])
        }
    except KeyError:
        raise ValueError(f"Unknown decoder_type '{decoder_type}'")


def get_pixel_data_decoders():
    """Return a :class:`dict` of ``{UID: callable}``."""
    return {
        val.name: val.load()
        for val in iter_entry_points('pylibjpeg.pixel_data_decoders')
    }


def _encode(arr, encoder=None, kwargs=None):
    """Return the encoded `arr` as a :class:`bytes`.

    .. versionadded:: 1.3.0

    Parameters
    ----------
    data : numpy.ndarray
        The image data to encode as a :class:`~numpy.ndarray`.
    decoder : callable, optional
        The plugin to use when encoding the data. If not used then all
        available encoders will be tried.
    kwargs : dict
        A ``dict`` containing keyword parameters to pass to the encoder.

    Returns
    -------
    bytes
        The encoded image data.

    Raises
    ------
    RuntimeError
        If `encoder` is not ``None`` and the corresponding plugin is not
        available.
    """
    encoders = get_encoders()
    if not encoders:
        raise RuntimeError("No encoders are available")

    kwargs = kwargs or {}

    if encoder is not None:
        try:
            return encoders[encoder](data, **kwargs)
        except KeyError:
            raise ValueError(f"The '{encoder}' encoder is not available")

    for name, encoders in encoders.items():
        try:
            return encoders(data, **kwargs)
        except Exception as exc:
            LOGGER.debug(f"Encoding with {name} plugin failed")
            LOGGER.exception(exc)

    # If we made it here then we were unable to encode the data
    raise ValueError("Unable to encode the data")


def get_encoders(encoder_type=None):
    """Return a :class:`dict` of JPEG encoders as {package: callable}.

    .. versionadded:: 1.3.0

    Parameters
    ----------
    encoder_type : str, optional
        The class of decoders to return, one of:

        * ``"JPEG"`` - ISO/IEC 10918 JPEG encoders
        * ``"JPEG XT"`` - ISO/IEC 18477 JPEG encoders
        * ``"JPEG-LS"`` - ISO/IEC 14495 JPEG encoders
        * ``"JPEG 2000"`` - ISO/IEC 15444 JPEG encoders
        * ``"JPEG XS"`` - ISO/IEC 21122 JPEG encoders
        * ``"JPEG XL"`` - ISO/IEC 18181 JPEG encoders

        If no `encoder_type` is used then all available encoders will be
        returned.

    Returns
    -------
    dict
        A dict of ``{'package_name': <encoder function>}``.
    """
    entry_points = {
        "JPEG" : "pylibjpeg.jpeg_encoders",
        "JPEG XT" : "pylibjpeg.jpeg_xt_encoders",
        "JPEG-LS" : "pylibjpeg.jpeg_ls_encoders",
        "JPEG 2000" : "pylibjpeg.jpeg_2000_encoders",
        "JPEG XR" : "pylibjpeg.jpeg_xr_encoders",
        "JPEG XS" : "pylibjpeg.jpeg_xs_encoders",
        "JPEG XL" : "pylibjpeg.jpeg_xl_encoders",
    }
    if encoder_type is None:
        encoders = {}
        for entry_point in entry_points.values():
            encoders.update({
                val.name: val.load() for val in iter_entry_points(entry_point)
            })
        return encoders

    try:
        return {
            val.name: val.load()
            for val in iter_entry_points(entry_points[encoder_type])
        }
    except KeyError:
        raise ValueError(f"Unknown encoder_type '{encoder_type}'")


def get_pixel_data_encoders():
    """Return a :class:`dict` of ``{UID: callable}``.

    .. versionadded:: 1.3.0
    """
    return {
        val.name: val.load()
        for val in iter_entry_points('pylibjpeg.pixel_data_encoders')
    }
