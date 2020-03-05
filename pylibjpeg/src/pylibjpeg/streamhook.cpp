// Includes
#include <iostream>
#include "streamhook.hpp"
#include "decode.hpp"
#include "utils.hpp"
#include "../libjpeg/interface/hooks.hpp"
#include "../libjpeg/interface/tagitem.hpp"
#include "../libjpeg/interface/parameters.hpp"
#include "../libjpeg/cmd/iohelpers.hpp"
#include "../libjpeg/tools/traits.hpp"
#include "std/stdio.hpp"
#include "std/stdlib.hpp"
#include "std/string.hpp"
#include "std/assert.hpp"


// The input stream hook function
JPG_LONG IStreamHook(struct JPG_Hook *hook, struct JPG_TagItem *tags)
{
    // Pointer to the input struct which is stored by the hook
    StreamData *in = (StreamData *)(hook->hk_pData);
    // Pointer to current pointer of the input buffer
    //   The pointer itself gets updated so no guarantee where it is
    char *data = (char *)(in->pData);

    switch(tags->GetTagData(JPGTAG_FIO_ACTION)) {
        case JPGFLAG_ACTION_READ:
        {
            UBYTE *buffer = (UBYTE *)tags->GetTagPtr(JPGTAG_FIO_BUFFER);
            ULONG  size   = (ULONG  )tags->GetTagData(JPGTAG_FIO_SIZE);

            // Number of bytes read this session
            ULONG bytes_read = 0;
            // Usually reads in 2048 bytes per run
            for (ULONG ii = 1; ii <= size; ii++) {
                // Check that we haven't gone beyond the buffer
                if (in->position >= in->length) {
                    break;
                }
                *buffer = *data;
                in->position += 1;
                bytes_read += 1;

                buffer++;
                data++;
            }
            // Update the stored pointer
            in->pData = data;

            return bytes_read;
        }
        case JPGFLAG_ACTION_WRITE:
        {
            UBYTE *buffer = (UBYTE *)tags->GetTagPtr(JPGTAG_FIO_BUFFER);
            ULONG  size   = (ULONG  )tags->GetTagData(JPGTAG_FIO_SIZE);

            // We want to raise an error so writing can be implemented
            return -1;
        }
        case JPGFLAG_ACTION_SEEK:
        {
            LONG mode   = tags->GetTagData(JPGTAG_FIO_SEEKMODE);
            LONG offset = tags->GetTagData(JPGTAG_FIO_OFFSET);

            // We want to raise an error here seek can be implemented
            switch(mode) {
                case JPGFLAG_OFFSET_CURRENT:
                    return -1;
                case JPGFLAG_OFFSET_BEGINNING:
                    return -1;
                case JPGFLAG_OFFSET_END:
                    return -1;
            }
            return -1;
        }
        case JPGFLAG_ACTION_QUERY:
        {
            return 0;
        }
    }
    return -1;
}


// The output stream hook function
JPG_LONG OStreamHook(struct JPG_Hook *hook, struct JPG_TagItem *tags)
{
    static ULONG OpenComponents = 0;
    struct StreamMemory *omm  = (struct StreamMemory *)(hook->hk_pData);
    struct StreamData *out = (struct StreamData *)(omm->omm_pTarget);
    // Pointer to the output numpy array, currently at offset out->position
    char *oArray = (char *)(out->pData);

    UWORD comp  = tags->GetTagData(JPGTAG_BIO_COMPONENT);
    ULONG miny  = tags->GetTagData((omm->omm_bUpsampling)?(JPGTAG_BIO_MINY):(JPGTAG_BIO_PIXEL_MINY));
    ULONG maxy  = tags->GetTagData((omm->omm_bUpsampling)?(JPGTAG_BIO_MAXY):(JPGTAG_BIO_PIXEL_MAXY));
    ULONG width = 1 + (tags->GetTagData((omm->omm_bUpsampling)?(JPGTAG_BIO_MAXX):(JPGTAG_BIO_PIXEL_MAXX)));

    assert(comp < omm->omm_usDepth);
    assert(maxy - miny < omm->omm_ulHeight);

    switch(tags->GetTagData(JPGTAG_BIO_ACTION)) {
        case JPGFLAG_BIO_REQUEST:
        {
            if (omm->omm_ucPixelType == CTYP_UBYTE) {
                UBYTE *mem = (UBYTE *)(omm->omm_pMemPtr);
                mem += comp;
                mem -= miny * omm->omm_usDepth * width;
                tags->SetTagPtr(JPGTAG_BIO_MEMORY        ,mem);
                tags->SetTagData(JPGTAG_BIO_WIDTH        ,width);
                tags->SetTagData(JPGTAG_BIO_HEIGHT       ,8 + miny);
                tags->SetTagData(JPGTAG_BIO_BYTESPERROW  ,omm->omm_usDepth * width * sizeof(UBYTE));
                tags->SetTagData(JPGTAG_BIO_BYTESPERPIXEL,omm->omm_usDepth * sizeof(UBYTE));
                tags->SetTagData(JPGTAG_BIO_PIXELTYPE    ,omm->omm_ucPixelType);
            } else if (omm->omm_ucPixelType == CTYP_UWORD) {
                UWORD *mem = (UWORD *)(omm->omm_pMemPtr);
                mem += comp;
                mem -= miny * omm->omm_usDepth * width;
                tags->SetTagPtr(JPGTAG_BIO_MEMORY        ,mem);
                tags->SetTagData(JPGTAG_BIO_WIDTH        ,width);
                tags->SetTagData(JPGTAG_BIO_HEIGHT       ,8 + miny);
                tags->SetTagData(JPGTAG_BIO_BYTESPERROW  ,omm->omm_usDepth * width * sizeof(UWORD));
                tags->SetTagData(JPGTAG_BIO_BYTESPERPIXEL,omm->omm_usDepth * sizeof(UWORD));
                tags->SetTagData(JPGTAG_BIO_PIXELTYPE    ,omm->omm_ucPixelType);
            } else if (omm->omm_ucPixelType == CTYP_FLOAT) {
                FLOAT *mem = (FLOAT *)(omm->omm_pMemPtr);
                mem += comp;
                mem -= miny * omm->omm_usDepth * width;
                tags->SetTagPtr(JPGTAG_BIO_MEMORY        ,mem);
                tags->SetTagData(JPGTAG_BIO_WIDTH        ,width);
                tags->SetTagData(JPGTAG_BIO_HEIGHT       ,8 + miny);
                tags->SetTagData(JPGTAG_BIO_BYTESPERROW  ,omm->omm_usDepth * width * sizeof(FLOAT));
                tags->SetTagData(JPGTAG_BIO_BYTESPERPIXEL,omm->omm_usDepth * sizeof(FLOAT));
                tags->SetTagData(JPGTAG_BIO_PIXELTYPE    ,omm->omm_ucPixelType);
            } else {
                tags->SetTagData(JPGTAG_BIO_PIXELTYPE    ,0);
            }

            // Read the source data.
            if (comp == 0) {
                ULONG height = maxy + 1 - miny;
                // Since we are here indicating the size of the available data,
                // clip to the eight lines available.
                if (height > 8)
                    height = 8;

                if (
                    omm->omm_ucPixelType == CTYP_UBYTE ||
                    omm->omm_ucPixelType == CTYP_UWORD ||
                    omm->omm_ucPixelType == CTYP_FLOAT
                )
                {
                    if (omm->omm_pLDRSource && omm->omm_pLDRMemPtr) {
                        // A designated LDR source is available. Read from
                        // here rather than using our primitive tone mapper.
                        fread(
                            omm->omm_pLDRMemPtr,
                            sizeof(UBYTE),
                            width * height * omm->omm_usDepth,
                            omm->omm_pLDRSource
                        );
                    }

                    if (omm->omm_pSource) {
                        if (omm->omm_bFloat) {
                            if (omm->omm_bNoOutputConversion) {
                                ULONG count = width * height * omm->omm_usDepth;
                                FLOAT *data = (FLOAT *)omm->omm_pMemPtr;
                                UBYTE *ldr  = (UBYTE *)omm->omm_pLDRMemPtr;
                                do {
                                    double in = readFloat(omm->omm_pSource,omm->omm_bBigEndian);
                                    UWORD half;
                                    if (omm->omm_bClamp && in < 0.0)
                                        in = 0.0;

                                    half = DoubleToHalf(in);
                                    // Tone-map the input unless there is an LDR source.
                                    if (omm->omm_pLDRMemPtr && omm->omm_pLDRSource == NULL)
                                        *ldr  = omm->omm_HDR2LDR[half];

                                    *data = FLOAT(in);
                                    data++,ldr++;
                                } while(--count);
                            } else {
                                ULONG count = width * height * omm->omm_usDepth;
                                UWORD *data = (UWORD *)omm->omm_pMemPtr;
                                UBYTE *ldr  = (UBYTE *)omm->omm_pLDRMemPtr;

                                do {
                                    double in = readFloat(omm->omm_pSource, omm->omm_bBigEndian);
                                    if (omm->omm_bClamp && in < 0.0)
                                        in = 0.0;

                                    *data = DoubleToHalf(in);
                                    // Tone-map the input unless there is an LDR source.
                                    if (omm->omm_pLDRMemPtr && omm->omm_pLDRSource == NULL) {
                                        if (in >= 0.0) {
                                            *ldr  = omm->omm_HDR2LDR[*data];
                                        } else {
                                            *ldr  = 0;
                                        }
                                    }
                                    data++,ldr++;
                                } while(--count);
                            }
                        } else {
                            fread(
                                omm->omm_pMemPtr,
                                omm->omm_ucPixelType & CTYP_SIZE_MASK,
                                width * height * omm->omm_usDepth,
                                omm->omm_pSource
                            );

                            #ifdef JPG_LIL_ENDIAN
                                // On those bloddy little endian machines, an endian swap is necessary
                                // as PNM is big-endian.
                                if (omm->omm_ucPixelType == CTYP_UWORD) {
                                    ULONG count = width * height * omm->omm_usDepth;
                                    UWORD *data = (UWORD *)omm->omm_pMemPtr;

                                    do {
                                        *data = (*data >> 8) | ((*data & 0xff) << 8);
                                        data++;
                                    } while(--count);
                                }
                            #endif

                            // Construct the tone-mapped LDR version of the image
                            // if there is no designated LDR input.
                            if (omm->omm_pLDRMemPtr && omm->omm_pLDRSource == NULL) {
                                if (omm->omm_ucPixelType == CTYP_UWORD) {
                                    ULONG count = width * height * omm->omm_usDepth;
                                    UWORD *data = (UWORD *)omm->omm_pMemPtr;
                                    UBYTE *ldr  = (UBYTE *)omm->omm_pLDRMemPtr;

                                    do {
                                        *ldr++ = omm->omm_HDR2LDR[*data++];
                                    } while(--count);
                                } else { // Huh, why tone mapping on 8 bit input? Ok, anyhow....
                                    ULONG count = width * height * omm->omm_usDepth;
                                    UBYTE *data = (UBYTE *)omm->omm_pMemPtr;
                                    UBYTE *ldr  = (UBYTE *)omm->omm_pLDRMemPtr;

                                    do {
                                        *ldr++ = omm->omm_HDR2LDR[*data++];
                                    } while(--count);
                                }
                            }
                        }
                    }
                }
            }

            assert((OpenComponents & (1UL << comp)) == 0);
            OpenComponents |= 1UL << comp;
        }
            break;
        case JPGFLAG_BIO_RELEASE:
        {
            // omm_ucPixelType: precision
            // omm_usDepth: number of components
            // omm_bFloat: input is floating point
            assert(OpenComponents & (1UL << comp));
            if (comp == omm->omm_usDepth - 1) {
                ULONG height = maxy + 1 - miny;
                if (
                    omm->omm_ucPixelType == CTYP_UBYTE ||
                    omm->omm_ucPixelType == CTYP_UWORD ||
                    omm->omm_ucPixelType == CTYP_FLOAT
                )
                {
                    if (oArray) {
                        if (omm->omm_bFloat) {
                            // No floating point input allowed for DICOM
                            if (omm->omm_bNoOutputConversion) {
                                ULONG count = width * height;
                                FLOAT *data = (FLOAT *)omm->omm_pMemPtr;
                                double r = 0.0, g = 0.0, b = 0.0;

                                do {
                                    switch(omm->omm_usDepth) {
                                        case 1:
                                            write_float(
                                                oArray,
                                                *data++,
                                                omm->omm_bBigEndian
                                            );
                                            break;
                                        case 3:
                                            r = *data++;
                                            g = *data++;
                                            b = *data++;
                                            write_float(oArray, r, omm->omm_bBigEndian);
                                            write_float(oArray, g, omm->omm_bBigEndian);
                                            write_float(oArray, b, omm->omm_bBigEndian);
                                            break;
                                    }
                                } while(--count);
                            } else {
                                ULONG count = width * height;
                                UWORD *data = (UWORD *)omm->omm_pMemPtr;
                                double r = 0.0, g = 0.0, b = 0.0;

                                do {
                                    switch(omm->omm_usDepth) {
                                        case 1:
                                            write_float(
                                                oArray,
                                                HalfToDouble(*data++),
                                                omm->omm_bBigEndian
                                            );
                                            break;
                                        case 3:
                                            r = HalfToDouble(*data++);
                                            g = HalfToDouble(*data++);
                                            b = HalfToDouble(*data++);
                                            write_float(oArray, r, omm->omm_bBigEndian);
                                            write_float(oArray, g, omm->omm_bBigEndian);
                                            write_float(oArray, b, omm->omm_bBigEndian);
                                            break;
                                    }
                                } while(--count);
                            }
                        } else {
                            // DICOM should always be integer input
                            // Write pixel data to target
                            ULONG size = omm->omm_ucPixelType & CTYP_SIZE_MASK;
                            ULONG count = width * height * omm->omm_usDepth;
                            UBYTE *mem = (UBYTE *)(omm->omm_pMemPtr);
                            // For each pixel
                            for (ULONG ii = 1; ii <= count; ii++) {
                                // For each byte of the pixel
                                for (ULONG jj = 1; jj <= size; jj++) {
                                    if (out->position >= out->length) {
                                        break;
                                    }
                                    // Write the byte value to the output
                                    *oArray = *mem;
                                    oArray++;
                                    out->position += 1;
                                    mem++;
                                }
                            }
                            // Update the buffer pointer
                            out->pData = oArray;
                        }
                    }
                }
            }
            OpenComponents &= ~(1UL << comp);
        }
        break;
    }
    return 0;
}
