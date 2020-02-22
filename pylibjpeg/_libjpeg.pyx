# cython: language_level=3
# distutils: language=c++

import numpy as np
cimport numpy as np

cdef extern from "decode.hpp":
    cdef void Decode(
        char *inArray, char *outArray, int inLength, int outLength,
    )


def decode(np.ndarray[np.uint8_t, ndim=1] input_buffer, nr_bytes):
    """Return the decoded JPEG data from `input_buffer`.

    Parameters
    ----------
    input_buffer : numpy.ndarray
        A 1D array of np.uint8 containing the raw encoded JPEG image.
    nr_bytes : int
        The expected length of the uncompressed image data in bytes.

    Returns
    -------
    numpy.ndarray
        A 1D array of np.uint8 containing the decoded image data.
    """
    # Pointer to first element in input array
    cdef char *pInput = <char *>np.PyArray_DATA(input_buffer)

    # Create array for output and get pointer to first element
    output_buffer = np.zeros(nr_bytes, dtype=np.uint8)
    cdef char *pOutput = <char *>np.PyArray_data(output_buffer)

    # Decode the data - output is written to output_buffer
    Decode(pInput, pOutput, input_buffer.shape[0], output_buffer.shape[0])

    return output_buffer
