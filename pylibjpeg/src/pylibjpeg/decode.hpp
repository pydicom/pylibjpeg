
#include <iostream>
#include <string>
#include "../libjpeg/interface/types.hpp"

#ifndef DECODE_HPP
#define DECODE_HPP

    // Prototypes
    // Decode the encoded JPEG file in `inArray` to `outArray`
    extern std::string Decode(
        char *inArray,
        char *outArray,
        int inLength,
        int outLength,
        int colourTransform
    );

    // Return the parameters of the encoded JPEG file in `inArray`
    extern std::string GetJPEGParameters(
        char *inArray, int inLength, struct JPEGParameters *param
    );

    struct StreamData {
        // Pointer to the current offset of the raw encoded JPEG byte data
        char *pData;
        // The current offset, starts at 0
        int position;
        // The total length of the byte data
        int length;
        // Pointer to the beginning of the byte data
        char *pStart;
        // Pointer to the end of the byte data
        char *pEnd;
    };

    struct JPEGParameters {
        ULONG columns;  // width in pixels
        ULONG rows;  // height in pixels
        UWORD samples_per_pixel;  // number of components
        UBYTE bits_per_sample;  // bit depth of input
    };

#endif
