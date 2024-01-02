import logging
import os
import sys

from importlib import metadata
from typing import BinaryIO, Any, Protocol, Union, Dict

import numpy as np


LOGGER = logging.getLogger(__name__)


DecodeSource = Union[str, os.PathLike, BinaryIO, bytes]


class Decoder(Protocol):
    def __call__(self, src: bytes, **kwargs: Any) -> np.ndarray:
        ...  # pragma: no cover


DECODER_ENTRY_POINTS = {
    "JPEG": "pylibjpeg.jpeg_decoders",
    "JPEG XT": "pylibjpeg.jpeg_xt_decoders",
    "JPEG-LS": "pylibjpeg.jpeg_ls_decoders",
    "JPEG 2000": "pylibjpeg.jpeg_2000_decoders",
    "JPEG XR": "pylibjpeg.jpeg_xr_decoders",
    "JPEG XS": "pylibjpeg.jpeg_xs_decoders",
    "JPEG XL": "pylibjpeg.jpeg_xl_decoders",
}


class Encoder(Protocol):
    def __call__(self, src: np.ndarray, **kwargs: Any) -> Union[bytes, bytearray]:
        ...  # pragma: no cover


ENCODER_ENTRY_POINTS = {
    "JPEG": "pylibjpeg.jpeg_encoders",
    "JPEG XT": "pylibjpeg.jpeg_xt_encoders",
    "JPEG-LS": "pylibjpeg.jpeg_ls_encoders",
    "JPEG 2000": "pylibjpeg.jpeg_2000_encoders",
    "JPEG XR": "pylibjpeg.jpeg_xr_encoders",
    "JPEG XS": "pylibjpeg.jpeg_xs_encoders",
    "JPEG XL": "pylibjpeg.jpeg_xl_encoders",
}


def decode(data: DecodeSource, decoder: str = "", **kwargs: Any) -> np.ndarray:
    """Return the decoded JPEG image as a :class:`numpy.ndarray`.

    Parameters
    ----------
    data : str, file-like, os.PathLike, or bytes
        The data to decode. May be a path to a file (as ``str`` or
        path-like), a file-like, or a ``bytes`` containing the encoded binary
        data.
    decoder : str, optional
        The name of the plugin to use when decoding the data. If not used
        then all available decoders will be tried.
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
        with open(str(data), "rb") as f:
            data = f.read()
    elif isinstance(data, bytes):
        pass
    else:
        # Try file-like
        data = data.read()

    if decoder:
        try:
            return decoders[decoder](data, **kwargs)
        except KeyError:
            raise ValueError(f"The '{decoder}' decoder is not available")

    for name, func in decoders.items():
        try:
            return func(data, **kwargs)
        except Exception as exc:
            LOGGER.debug(f"Decoding with {name} plugin failed")
            LOGGER.exception(exc)

    # If we made it here then we were unable to decode the data
    raise ValueError("Unable to decode the data")


def get_decoders(decoder_type: str = "") -> Dict[str, Decoder]:
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
    # TODO: Python 3.10 remove
    if sys.version_info[:2] < (3, 10):
        # {"package name": [EntryPoint(), ...]}
        ep = metadata.entry_points()
        if not decoder_type:
            decoders = {}
            for entry_point in DECODER_ENTRY_POINTS.values():
                print(entry_point in ep)
                if entry_point in ep:
                    decoders.update({val.name: val.load() for val in ep[entry_point]})

            return decoders

        if decoder_type in ep:
            return {val.name: val.load() for val in ep[decoder_type]}

        return {}

    if not decoder_type:
        decoders = {}
        for entry_point in DECODER_ENTRY_POINTS.values():
            result = metadata.entry_points(group=entry_point)
            decoders.update({val.name: val.load() for val in result})

        return decoders

    if decoder_type in DECODER_ENTRY_POINTS:
        result = metadata.entry_points(group=DECODER_ENTRY_POINTS[decoder_type])
        return {val.name: val.load() for val in result}

    return {}


def get_pixel_data_decoders() -> Dict[str, Decoder]:
    """Return a :class:`dict` of ``{UID: callable}``."""
    # TODO: Python 3.10 remove
    if sys.version_info[:2] < (3, 10):
        ep = metadata.entry_points()
        if "pylibjpeg.pixel_data_decoders" in ep:
            return {
                val.name: val.load()
                for val in ep["pylibjpeg.pixel_data_decoders"]
            }

        return {}

    return {
        val.name: val.load()
        for val in metadata.entry_points(group="pylibjpeg.pixel_data_decoders")
    }


def _encode(arr: np.ndarray, encoder: str = "", **kwargs: Any) -> Union[bytes, bytearray]:
    """Return the encoded `arr` as a :class:`bytes`.

    .. versionadded:: 1.3.0

    Parameters
    ----------
    data : numpy.ndarray
        The image data to encode as a :class:`~numpy.ndarray`.
    decoder : str, optional
        The name of the plugin to use when encoding the data. If not used then
        all available encoders will be tried.
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

    if encoder:
        try:
            return encoders[encoder](arr, **kwargs)
        except KeyError:
            raise ValueError(f"The '{encoder}' encoder is not available")

    for name, func in encoders.items():
        try:
            return func(arr, **kwargs)
        except Exception as exc:
            LOGGER.debug(f"Encoding with {name} plugin failed")
            LOGGER.exception(exc)

    # If we made it here then we were unable to encode the data
    raise ValueError("Unable to encode the data")


def get_encoders(encoder_type: str = "") -> Dict[str, Encoder]:
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
    # TODO: Python 3.10 remove
    if sys.version_info[:2] < (3, 10):
        ep = metadata.entry_points()
        if not encoder_type:
            encoders = {}
            for entry_point in ENCODER_ENTRY_POINTS.values():
                if entry_point in ep:
                    encoders.update({val.name: val.load() for val in ep[entry_point]})

            return encoders

        if encoder_type in ep:
            return {val.name: val.load() for val in ep[encoder_type]}

        return {}

    if not encoder_type:
        encoders = {}
        for entry_point in ENCODER_ENTRY_POINTS.values():
            result = metadata.entry_points().select(group=entry_point)
            encoders.update({val.name: val.load() for val in result})

        return encoders

    if encoder_type in ENCODER_ENTRY_POINTS:
        result = metadata.entry_points().select(group=ENCODER_ENTRY_POINTS[encoder_type])
        return {val.name: val.load() for val in result}

    return {}


def get_pixel_data_encoders() -> Dict[str, Encoder]:
    """Return a :class:`dict` of ``{UID: callable}``.

    .. versionadded:: 1.3.0
    """
    # TODO: Python 3.10 remove
    if sys.version_info[:2] < (3, 10):
        ep = metadata.entry_points()
        if "pylibjpeg.pixel_data_encoders" in ep:
            return {
                val.name: val.load()
                for val in ep["pylibjpeg.pixel_data_encoders"]
            }

        return {}

    return {
        val.name: val.load()
        for val in metadata.entry_points(group="pylibjpeg.pixel_data_encoders")
    }
