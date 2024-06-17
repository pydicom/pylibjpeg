from enum import IntEnum
from importlib import metadata
import logging
import os
from pathlib import Path
import sys
from typing import BinaryIO, Any, Protocol, Union, Dict, Tuple, cast

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
    def __call__(self, src: Union[np.ndarray, bytes], **kwargs: Any) -> Union[bytes, bytearray]:
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


class Version(IntEnum):
    v1 = 1
    v2 = 2


def decode(src: DecodeSource, decoder: str = "", **kwargs: Any) -> np.ndarray:
    """Return the decoded JPEG image as a :class:`numpy.ndarray`.

    Parameters
    ----------
    src : str, file-like, os.PathLike, or bytes
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
        raise RuntimeError(
            "No JPEG decoders are available - have you installed any plugins?"
        )

    if isinstance(src, (str, os.PathLike)):
        path = Path(src).resolve(strict=True)
        with path.open("rb") as f:
            data = f.read()
    elif isinstance(src, bytes):
        data = src
    else:
        # BinaryIO
        data = src.read()

    if decoder:
        try:
            return decoders[decoder](data, **kwargs)
        except KeyError:
            raise ValueError(
                f"The '{decoder}' decoder is not available - have you installed "
                "the plugin?"
            )
        except Exception as exc:
            LOGGER.debug(f"Decoding with the {decoder} plugin failed")
            LOGGER.exception(exc)

    for name, func in decoders.items():
        try:
            return func(data, **kwargs)
        except Exception as exc:
            LOGGER.debug(f"Decoding with the {name} plugin failed")
            LOGGER.exception(exc)

    # If we made it here then we were unable to decode the data
    raise ValueError("Unable to decode the data with the available plugins")


def _encode(
    arr: np.ndarray, encoder: str = "", **kwargs: Any
) -> Union[bytes, bytearray]:
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
        except Exception as exc:
            LOGGER.debug(f"Encoding with the {encoder} plugin failed")
            LOGGER.exception(exc)

    for name, func in encoders.items():
        try:
            return func(arr, **kwargs)
        except Exception as exc:
            LOGGER.debug(f"Encoding with the {name} plugin failed")
            LOGGER.exception(exc)

    # If we made it here then we were unable to encode the data
    raise ValueError("Unable to encode the data")


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
    decoders = cast(
        Dict[str, Decoder],
        _get_plugins(DECODER_ENTRY_POINTS, decoder_type),
    )
    return decoders


def get_encoders(encoder_type: str = "") -> Dict[str, Encoder]:
    """Return a :class:`dict` of JPEG encoders as {package: callable}.

    .. versionadded:: 1.3

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
    encoders = cast(
        Dict[str, Encoder],
        _get_plugins(ENCODER_ENTRY_POINTS, encoder_type),
    )
    return encoders


def _get_plugins(
    entry_points: Dict[str, str], plugin_type: str
) -> Dict[str, Union[Decoder, Encoder]]:
    """Return a :class:`dict` of JPEG encoders/decoders as {package: callable}.

    Parameters
    ----------
    entry_points : dict[str, str]
        A dict matching `plugin_type` to an entry point.
    plugin_type : str
        The class of encoders/decoders to return, one of:

        * ``"JPEG"`` - for ISO/IEC 10918 JPEG
        * ``"JPEG XT"`` - for ISO/IEC 18477 JPEG
        * ``"JPEG-LS"`` - for ISO/IEC 14495 JPEG
        * ``"JPEG 2000"`` - for ISO/IEC 15444 JPEG
        * ``"JPEG XS"`` - for ISO/IEC 21122 JPEG
        * ``"JPEG XL"`` - for ISO/IEC 18181 JPEG

        If no `plugin_type` is used then all available encoders/decoders will
        be returned.
    """
    plugins = {}

    # Python 3.8, 3.9
    if sys.version_info[:2] < (3, 10):
        # {"package name": [EntryPoint(), ...]}
        ep = metadata.entry_points()
        if not plugin_type:
            for entry_point in entry_points.values():
                eps = cast(Tuple[metadata.EntryPoint], ep.get(entry_point, tuple()))
                if eps:
                    names = sorted(list(set([f"'{x.name}'" for x in eps])))
                    LOGGER.debug(
                        f"Found plugin(s) {', '.join(names)} for entry point "
                        f"'{entry_point}'"
                    )
                    plugins.update({val.name: val.load() for val in eps})
                else:
                    LOGGER.debug(f"No plugins found for entry point '{entry_point}'")

            return plugins

        try:
            entry_point = entry_points[plugin_type]
        except KeyError:
            raise KeyError(f"No matching plugin entry point for '{plugin_type}'")

        eps = cast(Tuple[metadata.EntryPoint], ep.get(entry_point, tuple()))
        if eps:
            names = sorted(list(set([f"'{x.name}'" for x in eps])))
            LOGGER.debug(f"Found plugin(s) {names} for entry point '{entry_point}'")
        else:
            LOGGER.debug(f"No plugins found for entry point '{entry_point}'")

        return {val.name: val.load() for val in eps}

    # Python 3.10+
    if not plugin_type:
        for entry_point in entry_points.values():
            eps = metadata.entry_points(group=entry_point)
            if eps:
                names = sorted(list(set([f"'{x.name}'" for x in eps])))
                LOGGER.debug(
                    f"Found plugin(s) {', '.join(names)} for entry point "
                    f"'{entry_point}'"
                )
                plugins.update({val.name: val.load() for val in eps})
            else:
                LOGGER.debug(f"No plugins found for entry point '{entry_point}'")

        return plugins

    try:
        entry_point = entry_points[plugin_type]
    except KeyError:
        raise KeyError(f"No matching plugin entry point for '{plugin_type}'")

    eps = metadata.entry_points(group=entry_point)
    if eps:
        names = list(set([f"'{x.name}'" for x in eps]))
        LOGGER.debug(f"Found plugin(s) {names} for entry point '{entry_point}'")
    else:
        LOGGER.debug(f"No plugins found for entry point '{entry_point}'")

    return {val.name: val.load() for val in eps}


def get_pixel_data_decoders(
    version: int = Version.v1,
) -> Union[Dict[str, Decoder], Dict[str, Dict[str, Decoder]]]:
    """Return a :class:`dict` of ``{UID: callable}``.

    .. versionchanged:: 2.0

        Added the `version` parameter to support returning multiple decoders
        for the same UID.

    Parameters
    ----------
    version : int, optional
        If ``1`` (default) then return available decoding functions as
        ``{UID: func}``, otherwise return the available decoding functions as
        ``{UID: {plugin name: func}}``.

    Returns
    -------
    dict[str, Decoder] | dict[str, dict[str, Decoder]]
        A dict containing the available plugins as:

        * ``{UID: decoding function}`` for `version` ``1``
        * ``{UID: {plugin name: decoding function}}`` for `version` ``2``
    """

    entry_point = "pylibjpeg.pixel_data_decoders"
    decoders = cast(
        Union[
            Dict[str, Union[Decoder, Encoder]],
            Dict[str, Dict[str, Union[Decoder, Encoder]]],
        ],
        _get_pixel_data_plugins(entry_point, version),
    )
    return decoders


def get_pixel_data_encoders(
    version: int = Version.v1,
) -> Union[Dict[str, Encoder], Dict[str, Dict[str, Encoder]]]:
    """Return a :class:`dict` of ``{UID: callable}``.

    .. versionadded:: 1.3.0

    .. versionchanged:: 2.0

        Added the `version` parameter to support returning multiple encoders
        for the same UID.

    Parameters
    ----------
    version : int, optional
        If ``1`` (default) then return available encoding functions as
        ``{UID: func}``, otherwise return the available encoding functions as
        ``{UID: {plugin name: func}}``.

    Returns
    -------
    dict[str, Decoder] | dict[str, dict[str, Decoder]]
        A dict containing the available plugins as:

        * ``{UID: encoding function}`` for `version` ``1``
        * ``{UID: {plugin name: encoding function}}`` for `version` ``2``
    """
    entry_point = "pylibjpeg.pixel_data_encoders"
    encoders = cast(
        Union[Dict[str, Encoder], Dict[str, Dict[str, Encoder]]],
        _get_pixel_data_plugins(entry_point, version),
    )
    return encoders


def _get_pixel_data_plugins(
    entry_point: str,
    version: int,
) -> Union[
    Dict[str, Union[Decoder, Encoder]], Dict[str, Dict[str, Union[Decoder, Encoder]]]
]:
    """Return the available functions for `entry_point`.

    Parameters
    ----------
    entry_point : str
        The name of the entry point of the plugins.
    version : int
        If ``1`` then return available functions as ``{UID: func}``,
        otherwise return the available functions as ``{UID: {plugin name: func}}``.

    Returns
    -------
    dict[str, Decoder] | dict[str, dict[str, Decoder]]
        A dict containing the available plugins as:

        * ``{UID: function}`` for `version` ``1``
        * ``{UID: {plugin name: function}}`` for `version` ``2``
    """
    plugins = {}

    # Python 3.8, 3.9
    if sys.version_info[:2] < (3, 10):
        entry_points = metadata.entry_points()
        if entry_point not in entry_points:
            LOGGER.debug(f"No plugins found for entry point '{entry_point}'")
            return {}

        # dict[str, Tuple[EntryPoint]], may be multiple EntryPoints for same UID
        eps = entry_points[entry_point]
        LOGGER.debug(f"Found plugin(s) for entry point '{entry_point}'")
        for ep in set(eps):
            name = ep.value.split(":")[0]
            LOGGER.debug(f"  Found plugin '{name}' for UID '{ep.name}'")
            if version == Version.v1:
                # Return {UID: encode/decode function}
                plugins[ep.name] = ep.load()
            else:
                # Return {UID: {plugin name: encode/decode function}}
                uid_plugins = plugins.setdefault(ep.name, {})
                uid_plugins[name] = ep.load()

        return plugins

    # Python 3.10+
    eps = metadata.entry_points(group=entry_point)
    if not eps:
        LOGGER.debug(f"No plugins found for entry point '{entry_point}'")
        return {}

    LOGGER.debug(f"Found plugin(s) for entry point '{entry_point}'")
    for ep in set(eps):
        name = ep.value.split(":")[0]
        LOGGER.debug(f"  Found plugin '{name}' for UID '{ep.name}'")
        if version == Version.v1:
            # Return {UID: encode/decode function}
            plugins[ep.name] = ep.load()
        else:
            # Return {UID: {plugin name: encode/decode function}}
            uid_plugins = plugins.setdefault(ep.name, {})
            uid_plugins[name] = ep.load()

    return plugins
