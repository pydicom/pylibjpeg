#cython: language_level=3
# distutils: language=c++

from libcpp cimport bool

import numpy as np
cimport numpy as np

cdef extern from "cmd/reconstruct.hpp":
    cdef void Reconstruct(
        char *infile,
        char *outfile,
        int colortrafo,  # int colortrafo = JPGFLAG_MATRIX_COLORTRANSFORMATION_YCBCR
        char *alpha,  # const char *alpha = NULL input/output source for alpha channel
        bool upsample  # bool upstream = true
    )


def decode(infile, outfile):
    Reconstruct(infile, outfile, 1, NULL, True)
