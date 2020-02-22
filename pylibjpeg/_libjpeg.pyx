#cython: language_level=3
# distutils: language=c++

import numpy as np
cimport numpy as np

cdef extern from "decode.hpp":
    cdef void Decode(
        char *infile,
        char *outfile,
        int in_length,
        int out_length,
    )


def decode(np.ndarray[np.uint8_t, ndim=1] input_buffer, outfile, nr_bytes):
    """
    """
    # Pointer to first element in input array
    cdef char *pInput = <char *>np.PyArray_DATA(input_buffer)

    # Create array for output and get pointer to first element
    output_buffer = np.ndarray(nr_bytes, dtype=np.uint8)
    cdef char *pOutput = <char *>np.PyArray_data(output_buffer)

    # Decode the data
    Decode(pInput, pOutput, input_buffer.shape[0], output_buffer.shape[0])

    return output_buffer
