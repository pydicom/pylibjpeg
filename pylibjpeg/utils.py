
import logging
import os
from pkg_resources import iter_entry_points
from struct import unpack

import numpy as np


LOGGER = logging.getLogger(__name__)


def add_handler():
    """Add the pixel data handler to *pydicom*.

    Raises
    ------
    ImportError
        If *pydicom* is not available.
    """
    from .pydicom import pixel_data_handler as handler
    import pydicom.config

    if handler not in pydicom.config.pixel_data_handlers:
        pydicom.config.pixel_data_handlers.append(handler)


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
            raise ValueError(
                "The '{}' decoder is not available".format(decoder)
            )

    for name, decoder in decoders.items():
        try:
            return decoder(data, **kwargs)
        except Exception as exc:
            LOGGER.debug("Decoding with {} plugin failed".format(name))
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
        raise ValueError("Unknown decoder_type '{}'".format(decoder_type))


def remove_handler():
    """Remove the pixel data handler from *pydicom*.

    Raises
    ------
    ImportError
        If *pydicom* is not available.
    """
    from .pydicom import pixel_data_handler as handler
    import pydicom.config

    if handler in pydicom.config.pixel_data_handlers:
        pydicom.config.pixel_data_handlers.remove(handler)
