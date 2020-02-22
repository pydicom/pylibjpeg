
#ifndef DECODE_HPP
#define DECODE_HPP

    // Prototypes
    extern void Decode(
        char *inArray, char *outArray, int inLength, int outLength
    );

    struct StreamData{
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

#endif
