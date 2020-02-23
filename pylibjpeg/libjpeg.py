
import _libjpeg


def decode(arr, nr_bytes):
    """Return the decoded JPEG data from `arr`.

    Parameters
    ----------
    arr : numpy.ndarray
        A 1D array of np.uint8 containing the raw encoded JPEG image.
    nr_bytes : int
        The expected length of the uncompressed image data in bytes.

    Returns
    -------
    numpy.ndarray
        A 1D array of np.uint8 containing the decoded image data.
    """
    return _libjpeg.decode(arr, nr_bytes)


def add_handler():
    """Add the pylibjpeg pixel data handler to pydicom.

    Raises
    ------
    ImportError
        If *pydicom* is not available.
    """
    # Avoid circular import during unit testing
    from . import libjpeg_handler
    import pydicom.config

    if libjpeg_handler not in pydicom.config.pixel_data_handlers:
        pydicom.config.pixel_data_handlers.append(libjpeg_handler)


def remove_handler():
    """Remove the pylibjpeg pixel data handler from pydicom.

    Raises
    ------
    ImportError
        If *pydicom* is not available.
    """
    # Avoid circular import during unit testing
    from . import libjpeg_handler
    import pydicom.config

    if libjpeg_handler in pydicom.config.pixel_data_handlers:
        pydicom.config.pixel_data_handlers.remove(libjpeg_handler)
