
import _libjpeg


def decode(arr, nr_bytes, colourspace='YBR_FULL'):
    """Return the decoded JPEG data from `arr`.

    Parameters
    ----------
    arr : numpy.ndarray
        A 1D array of np.uint8 containing the raw encoded JPEG image.
    nr_bytes : int
        The expected length of the uncompressed image data in bytes.
    colourspace : str, optional
        One of 'MONOCHROME1', 'MONOCHROME2', 'RGB', 'YBR_FULL', 'YBR_FULL_422',
        'RCT', 'ICT'.

    Returns
    -------
    numpy.ndarray
        A 1D array of np.uint8 containing the decoded image data.
    """
    colours = {
        'MONOCHROME1': 0,
        'MONOCHROME2' : 0,
        'RGB' : 1,
        'YBR_FULL' : 0,
        'YBR_FULL_422' : 0,
        'RCT' : 2,
        'ICT' : 3,
    }

    try:
        transform = colours[colourspace]
    except KeyError:
        warnings.warn("")
        transform = 0

    return _libjpeg.decode(arr, nr_bytes, transform)


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
