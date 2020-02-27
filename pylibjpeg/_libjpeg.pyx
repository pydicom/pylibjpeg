# cython: language_level=3
# distutils: language=c++

from math import ceil

from libcpp cimport bool
from libcpp.string cimport string

import numpy as np
cimport numpy as np


cdef extern from "decode.hpp":
    cdef string Decode(
        char *inArray,
        char *outArray,
        int inLength,
        int outLength,
        int colourspace,
    )

    cdef struct JPEGParameters:
        int marker
        long columns
        long rows
        int samples_per_pixel
        char bits_per_sample

    cdef string GetJPEGParameters(
        char *inArray,
        int inLength,
        JPEGParameters *param,
    )


def decode(np.ndarray[np.uint8_t, ndim=1] input_buffer, colourspace):
    """Return the decoded JPEG data from `input_buffer`.

    Parameters
    ----------
    input_buffer : numpy.ndarray
        A 1D array of ``np.uint8`` containing the raw encoded JPEG image.
    colourspace : int
        | ``0`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_NONE``
        | ``1`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_YCBCR``
        | ``2`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_LSRCT``
        | ``2`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_RCT``
        | ``3`` : ``JPGFLAG_MATRIX_COLORTRANSFORMATION_FREEFORM``

    Returns
    -------
    bytes
        The status and any error message of the decoding operation.
    numpy.ndarray or None
        A 1D array of ``np.uint8`` containing the decoded image data. Returns
        ``None`` if the decode fails.
    dict
        A :class:`dict` containing the image parameters.
    """
    # Get the image parameters
    status, param = get_parameters(input_buffer)

    # Pointer to first element in input array
    cdef char *pInput = <char *>np.PyArray_DATA(input_buffer)

    # Create array for output and get pointer to first element
    bpp = ceil(param['bits_per_sample'] / 8)
    nr_bytes = (
        param['rows'] * param['columns'] * param['samples_per_pixel'] * bpp
    )
    output_buffer = np.zeros(nr_bytes, dtype=np.uint8)
    cdef char *pOutput = <char *>np.PyArray_DATA(output_buffer)

    # Decode the data - output is written to output_buffer
    status = Decode(
        pInput,
        pOutput,
        input_buffer.shape[0],
        output_buffer.shape[0],
        colourspace
    )

    return status, output_buffer, param


def get_parameters(np.ndarray[np.uint8_t, ndim=1] input_buffer):
    """Return a :class:`dict` containing the JPEG image parameters.

    Parameters
    ----------
    input_buffer : numpy.ndarray
        A 1D array of ``np.uint8`` containing the encoded JPEG image.

    Returns
    -------
    dict
        A :class:`dict` containing the JPEG image parameters.
    """
    cdef JPEGParameters param
    param.columns = 0
    param.rows = 0
    param.samples_per_pixel = 0
    param.bits_per_sample = 0

    # Pointer to the JPEGParameters object
    cdef JPEGParameters *pParam = &param

    # Pointer to first element in input array
    cdef char *pInput = <char *>np.PyArray_DATA(input_buffer)

    # Decode the data - output is written to output_buffer
    status = GetJPEGParameters(
        pInput,
        input_buffer.shape[0],
        pParam
    )

    parameters = {
        'rows' : param.rows,
        'columns' : param.columns,
        'samples_per_pixel' : param.samples_per_pixel,
        'bits_per_sample' : param.bits_per_sample,
    }

    return status, parameters


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
