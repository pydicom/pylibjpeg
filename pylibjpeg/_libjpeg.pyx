# cython: language_level=3
# distutils: language=c++

from libcpp cimport bool

import numpy as np
cimport numpy as np


cdef extern from "decode.hpp":
    cdef void Decode(
        char *inArray,
        char *outArray,
        int inLength,
        int outLength,
        int colourspace,
    )


def decode(np.ndarray[np.uint8_t, ndim=1] input_buffer, nr_bytes, colourspace):
    """Return the decoded JPEG data from `input_buffer`.

    Parameters
    ----------
    input_buffer : numpy.ndarray
        A 1D array of np.uint8 containing the raw encoded JPEG image.
    nr_bytes : int
        The expected length of the uncompressed image data in bytes.
    colourspace : int
        | ``0`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_NONE``
        | ``1`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_YCBCR``
        | ``2`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_LSRCT``
        | ``2`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_RCT``
        | ``3`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_FREEFORM``

    Returns
    -------
    numpy.ndarray
        A 1D array of np.uint8 containing the decoded image data.
    """
    # Pointer to first element in input array
    cdef char *pInput = <char *>np.PyArray_DATA(input_buffer)

    # Create array for output and get pointer to first element
    output_buffer = np.zeros(nr_bytes, dtype=np.uint8)
    cdef char *pOutput = <char *>np.PyArray_DATA(output_buffer)

    # Decode the data - output is written to output_buffer
    Decode(
        pInput,
        pOutput,
        input_buffer.shape[0],
        output_buffer.shape[0],
        colourspace
    )

    return output_buffer


cdef extern from "cmd/reconstruct.hpp":
    cdef void Reconstruct(
        const char *inArray,
        const char *outArray,
        int colortrafo,
        const char *alpha,
        bool upsample,
    )


def reconstruct(fin, fout, colourspace, falpha, upsample):
    """Decode the JPEG file in `fin` and write it to `fout` as PNM.

    Parameters
    ----------
    fin : bytes
        The path to the JPEG file to be decoded.
    fout : bytes
        The path to the decoded PNM file.
    colourspace : int
        The colourspace transform to apply.
    falpha : bytes or None
        The path where any decoded alpha channel data will be written,
        otherwise ``None`` to not write alpha channel data. Equivalent to the
        ``-al file`` flag.
    upsample : bool
        ``True`` to disable automatic upsampling, equivalent to the ``-U``
        flag.
    """
    if falpha is None:
        Reconstruct(fin, fout, colourspace, NULL, upsample)
    else:
        Reconstruct(fin, fout, colourspace, falpha, upsample)
