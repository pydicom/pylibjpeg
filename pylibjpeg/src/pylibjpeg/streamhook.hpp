#ifndef PYLIBJPEG_STREAMHOOK_HPP
#define PYLIBJPEG_STREAMHOOK_HPP

// Includes
#include "../libjpeg/interface/types.hpp"
#include "std/stdio.hpp"
#include "decode.hpp"


// Forwards
struct JPG_Hook;
struct JPG_TagItem;


// Prototypes
// Handler for the input and output stream hooks
extern JPG_LONG IStreamHook(struct JPG_Hook *hook, struct JPG_TagItem *tags);
extern JPG_LONG OStreamHook(struct JPG_Hook *hook, struct JPG_TagItem *tags);

/// Administration of output stream
struct StreamMemory {
    APTR         omm_pMemPtr;     // interleaved memory for the HDR image
    APTR         omm_pLDRMemPtr;  // interleaved memory for the LDR version of the image
    APTR         omm_pAlphaPtr;   // memory for the alpha channel
    ULONG        omm_ulWidth;     // width in pixels.
    ULONG        omm_ulHeight;    // height in pixels; this is only one block in our application.
    UWORD        omm_usDepth;     // number of components.
    UBYTE        omm_ucPixelType; // precision etc.
    UBYTE        omm_ucAlphaType; // pixel type of the alpha channel
    StreamData        *omm_pTarget;     // where to write the data to.
    FILE        *omm_pSource;     // where the data comes from on reading (encoding)
    FILE        *omm_pLDRSource;  // if there is a separate source for the LDR image, this is non-NULL.
    // TODO: output alpha to numpy array
    FILE        *omm_pAlphaTarget;// where the alpha (if any) goes to on decoding
        FILE        *omm_pAlphaSource;// where the alpha data (if any) comes from. There is no dedicated alpha LDR file
    const UWORD *omm_HDR2LDR;     // the (simple global) tone mapper used for encoding the image.
    bool         omm_bFloat;      // is true if the input is floating point
    bool         omm_bAlphaFloat; // is true if the opacity information is floating point
    bool         omm_bBigEndian;  // is true if the floating point input is big endian
    bool         omm_bAlphaBigEndian;     // if true, the floating point alpha channel is big endian
    bool         omm_bNoOutputConversion; // if true, the FLOAT stays float and the half-map is not applied.
    bool         omm_bNoAlphaOutputConversion; // ditto for alpha
    bool         omm_bClamp;      // if set, clamp negative values to zero.
    bool         omm_bAlphaClamp; // if set, alpha values outside [0,1] will be clamped to range
    bool         omm_bUpsampling; // if set, data is already upsampled.
};

#endif
