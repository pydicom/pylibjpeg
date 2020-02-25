
import pathlib
import warnings

import _libjpeg


LIBJPEG_ERROR_CODES = {
    -1024 : "A parameter for a function was out of range",
    -1025 : "Stream run out of data",
    -1026 : "A code block run out of data",
    -1027 : "Tried to perform an unputc or or an unget on an empty stream",
    -1028 : "Some parameter run out of range",
    -1029 : "The requested operation does not apply",
    -1030 : "Tried to create an already existing object",
    -1031 : "Tried to access a non-existing object",
    -1032 : "A non-optional parameter was left out",
    -1033 : "Forgot to delay a 0xFF",
    -1034 : (
        "Internal error: the requested operation is not available"
    ),
    -1035 : (
        "Internal error: an item computed on a former pass does not "
        "coincide with the same item on a later pass"
    ),
    -1036 : "The stream passed in is no valid jpeg stream",
    -1037 : (
        "A unique marker turned up more than once. The input stream is "
        "most likely corrupt"
    ),
    -1038 : "A misplaced marker segment was found",
    -1040 : (
        "The specified parameters are valid, but are not supported by "
        "the selected profile. Either use a higher profile, or use "
        "simpler parameters (encoder only). "
    ),
    -1041 : (
        "Internal error: the worker thread that was currently active had "
        "to terminate unexpectedly"
    ),
    -1042 : (
        "The encoder tried to emit a symbol for which no Huffman code "
        "was defined. This happens if the standard Huffman table is used "
        "for an alphabet for which it was not defined. The reaction "
        "to this exception should be to create a custom huffman table "
        "instead"
    ),
    -2046 : "Failed to construct the JPEG object",
}


def add_handler():
    """Add the pylibjpeg pixel data handler to pydicom.

    Raises
    ------
    ImportError
        If *pydicom* is not available.
    """
    # Avoid circular import during unit testing
    import pydicom.config
    from . import libjpeg_handler

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
        One of 'MONOCHROME1', 'MONOCHROME2', 'RGB', 'YBR_FULL', 'YBR_FULL_422'.

    Returns
    -------
    numpy.ndarray
        A 1D array of np.uint8 containing the decoded image data.

    Raises
    ------
    RuntimeError
        If the decoding failed.
    """
    colours = {
        'MONOCHROME1': 0,
        'MONOCHROME2' : 0,
        'RGB' : 1,
        'YBR_FULL' : 0,
        'YBR_FULL_422' : 0,
    }

    try:
        transform = colours[colourspace]
    except KeyError:
        warnings.warn(
            "Unsupported colour space '{}', no colour transform will "
            "be applied".format(colourspace)
        )
        transform = 0

    status, out = _libjpeg.decode(arr, nr_bytes, transform)
    status = status.decode("utf-8")
    code, msg = status.split("::::")
    code = int(code)

    if code == 0:
        return out

    try:
        raise RuntimeError(
            "libjpeg error code '{}' returned from Decode(): {} - {}"
            .format(code, LIBJPEG_ERROR_CODES[code], msg)
        )
    except KeyError:
        pass

    raise RuntimeError(
        "Unknown error code '{}' returned from Decode(): {}"
        .format(status, msg)
    )


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
    import pydicom.config
    from . import libjpeg_handler

    if libjpeg_handler in pydicom.config.pixel_data_handlers:
        pydicom.config.pixel_data_handlers.remove(libjpeg_handler)
