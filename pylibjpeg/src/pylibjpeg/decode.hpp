
#ifndef DECODE_HPP
#define DECODE_HPP

    // Prototypes
    extern void Decode(
        char *inArray, const char *outArray, int inLength, int outLength
    );

    struct StreamData{
        // The raw encoded JPEG byte data
        char *pData;
        // The current offset, starts at 0
        int position;
        // The number of bytes read
        int nr_read;
        // The total length of the byte data
        int length;
        // Pointer to the beginning of the byte data
        char *pStart;
        // Pointer to the end of the byte data
        char *pEnd;
    };

#endif
