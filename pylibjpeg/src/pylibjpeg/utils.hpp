
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
        //putc(u.long_buf >> 16, out);
        //putc(u.long_buf >>  8, out);
        //putc(u.long_buf >>  0, out);
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
