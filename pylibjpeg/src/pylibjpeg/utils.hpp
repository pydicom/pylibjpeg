// Copyright 2020 pylibjpeg contributors
//
// This work is licensed under GPL-3.0-only, see LICENSE.txt for details.

#include "decode.hpp"

void inline write_float(char *out, FLOAT f, bool bigendian)
{
    union {
        LONG  long_buf;
        FLOAT float_buf;
    } u;

    u.float_buf = f;

    if (bigendian) {
        *out = u.long_buf >> 24;
        out++;
        *out = u.long_buf >> 16;
        out++;
        *out = u.long_buf >> 8;
        out++;
        *out = u.long_buf >> 0;
        out++;
    } else {
        *out = u.long_buf >>  0;
        out++;
        *out = u.long_buf >>  8;
        out++;
        *out = u.long_buf >>  16;
        out++;
        *out = u.long_buf >>  24;
        out++;
    }
}
