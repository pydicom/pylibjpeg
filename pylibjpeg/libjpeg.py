
import pathlib

import _libjpeg


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


def decode(arr, nr_bytes, colourspace='YBR_FULL'):
    """Return the decoded JPEG data from `arr` as a 1D numpy array.

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


def reconstruct(fin, fout, colourspace=1, falpha=None, upsample=True):
    """Simple wrapper for the libjpeg cmd/reconstruct::Reconstruct() function.

    Parameters
    ----------
    fin : bytes
        The path to the JPEG file to be decoded.
    fout : bytes
        The path to the decoded PPM or PGM (is `falpha` is ``True``) file(s).
    colourspace : int, optional
        The colourspace transform to apply.
        | ``0`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_NONE``  (``-c`` flag)
        | ``1`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_YCBCR`` (default)
        | ``2`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_LSRCT`` (``-cls`` flag)
        | ``2`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_RCT``
        | ``3`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_FREEFORM``
        See `here<https://github.com/thorfdbg/libjpeg/blob/87636f3b26b41b85b2fb7355c589a8c456ef808c/interface/parameters.hpp#L381>`_
        for more information.
    falpha : bytes, optional
        The path where any decoded alpha channel data will be written (as a
        PGM file), otherwise ``None`` (default) to not write alpha channel
        data. Equivalent to the ``-al file`` flag.
    upsample : bool, optional
        ``True`` (default) to disable automatic upsampling, equivalent to
        the ``-U`` flag.
    """
    if isinstance(fin, (str, pathlib.Path)):
        fin = str(fin)
        fin = bytes(fin, 'utf-8')

    if isinstance(fout, (str, pathlib.Path)):
        fout = str(fout)
        fout = bytes(fout, 'utf-8')

    if falpha and isinstance(falpha, (str, pathlib.Path)):
        falpha = str(falpha)
        falpha = bytes(falpha, 'utf-8')

    _libjpeg.reconstruct(fin, fout, colourspace, falpha, upsample)


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
