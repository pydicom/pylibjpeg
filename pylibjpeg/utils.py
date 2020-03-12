
import logging
import os

import numpy as np

from .plugins import get_decoders


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
    kwargs : dict
        A ``dict`` containing keyword parameters to pass to the decoder.
    decoder : callable, optional
        The plugin to use when decoding the data. Should be ``'libjpeg'``
        or ``'openjpeg'``. If not used then all available decoders will be
        tried.

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
            data = np.frombuffer(f.read(), 'uint8')
    elif isinstance(data, bytes):
        data = np.frombuffer(data, 'uint8')
    else:
        # Try file-like
        data = np.frombuffer(data.read(), 'uint8')

    kwargs = kwargs or {}

    # Test plugin is available
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
