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
    // Pointer to the input data which is stored by the hook
    // Need to customise the hook so we can add the length of the input data
    StreamData *in = (StreamData *)(hook->hk_pData);
    char *data = (char *)(in->pData);

    std::cout << "Current position: " << in->position << std::endl;
    std::cout << "Moving pointer to position" << std::endl;
    printf("Initial position 0x%X, value 0x%X\n", data, *data);
    // init, condition, increase
    // repeats while condition is true
    int total_move = 0;
    for (int ii = 0; ii < in->position; ii++) {
        total_move += 1;
        data++;
    }
    std::cout << "Moved " << total_move << std::endl;
    printf("Final position 0x%X, value 0x%X\n", data, *data);

    switch(tags->GetTagData(JPGTAG_FIO_ACTION)) {
        case JPGFLAG_ACTION_READ:
        {
            UBYTE *buffer = (UBYTE *)tags->GetTagPtr(JPGTAG_FIO_BUFFER);
            ULONG  size   = (ULONG  )tags->GetTagData(JPGTAG_FIO_SIZE);

            std::cout << "Reading " << size << " bytes starting at " << in->position << std::endl;

            // Number of bytes read this session
            ULONG bytes_read = 0;
            // TODO dont allow reading beyond end
            for (int ii = 0; ii < size; ii++) {
                if (in->nr_read >= in->length) {
                    break;
                }
                //std::cout << *in << std::endl;
                // Copy value at current input item to buffer
                *buffer = *data;
                in->nr_read += 1;
                in->position += 1;
                bytes_read += 1;
                // Increment buffer pointer
                buffer++;
                // Increment input pointer
                data++;
            }

            std::cout << "Read " << bytes_read << " now at " << in->position << std::endl;

            //int nr_read = fread(buffer, 1, size, in);
            //std::cout << "read " << bytes_read << " total " << in->nr_read << std::endl;
            return bytes_read;
        }
        case JPGFLAG_ACTION_WRITE:
        {
            UBYTE *buffer = (UBYTE *)tags->GetTagPtr(JPGTAG_FIO_BUFFER);
            ULONG  size   = (ULONG  )tags->GetTagData(JPGTAG_FIO_SIZE);

            std::cout << "Need to write" << std::endl;

            /*
            std::cout << "writing... \n";
            int nr_write = fwrite(buffer, 1, size, in);
            std::cout << "write " << nr_write << std::endl;
            return nr_write;
            */
            return 0;
        }
        case JPGFLAG_ACTION_SEEK:
        {
            LONG mode   = tags->GetTagData(JPGTAG_FIO_SEEKMODE);
            LONG offset = tags->GetTagData(JPGTAG_FIO_OFFSET);

            std::cout << "Current position " << in->position << std::endl;
            std::cout << "Move " << offset;

            int result = 0;
            switch(mode) {
                case JPGFLAG_OFFSET_CURRENT:
                    std::cout << " from current" << std::endl;
                    for (int ii = 0; ii <= offset; ii++)
                    {
                        data++;
                        in->position += 1;
                    }
                    return result;
                case JPGFLAG_OFFSET_BEGINNING:
                    std::cout << " from start" << std::endl;
                    //for (int ii = 0; ii < offset, ii++) {
                    //    //
                    //}
                    return result;
                case JPGFLAG_OFFSET_END:
                    std::cout << " from end" << std::endl;
                    return result;
            }
            return 0;
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
    char *oArray = (char *)(out->pData);

    std::cout << "Current position: " << out->position << std::endl;
    std::cout << "Moving pointer to position" << std::endl;
    int total_move = 0;
    for (int ii = 0; ii < out->position; ii++) {
        total_move += 1;
        oArray++;
    }
    std::cout << "Moved " << total_move << std::endl;

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
                // Since we are here indicating the size of the available data, clip to the eight
                // lines available.
                if (height > 8)
                    height = 8;

                if (
                    omm->omm_ucPixelType == CTYP_UBYTE ||
                    omm->omm_ucPixelType == CTYP_UWORD ||
                    omm->omm_ucPixelType == CTYP_FLOAT
                )
                {
                    if (omm->omm_pLDRSource && omm->omm_pLDRMemPtr) {
                        // A designated LDR source is available. Read from here rather than using
                        // our primitive tone mapper.
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
            assert(OpenComponents & (1UL << comp));
            // PGX writes plane-interleaved, not line-interleaved.
            //if (omm->omm_bWritePGX || comp == omm->omm_usDepth - 1) {
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
                            if (omm->omm_bNoOutputConversion) {
                                ULONG count = width * height;
                                FLOAT *data = (FLOAT *)omm->omm_pMemPtr;
                                double r = 0.0, g = 0.0, b = 0.0;

                                do {
                                    /*
                                    if (omm->omm_bWritePGX) {
                                        writeFloat(
                                            omm->omm_PGXFiles[comp],
                                            data[comp],
                                            omm->omm_bBigEndian
                                        );
                                        data += omm->omm_usDepth;
                                    } else switch(omm->omm_usDepth) {
                                    */
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
                                    /*
                                    if (omm->omm_bWritePGX) {
                                        writeFloat(
                                            omm->omm_PGXFiles[comp],
                                            HalfToDouble(data[comp]),
                                            omm->omm_bBigEndian
                                        );
                                        data += omm->omm_usDepth;
                                    } else switch(omm->omm_usDepth) {
                                    */
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
                            /*
                            if (omm->omm_bWritePGX) {
                                if (omm->omm_ucPixelType == CTYP_UWORD) {
                                    UWORD *data = (UWORD *)omm->omm_pMemPtr;
                                    ULONG count = width * height;

                                    do {
                                        fputc(data[comp] >> 8,omm->omm_PGXFiles[comp]);
                                        fputc(data[comp]     ,omm->omm_PGXFiles[comp]);
                                        data += omm->omm_usDepth;
                                    } while(--count);
                                } else {
                                    UBYTE *data = (UBYTE *)omm->omm_pMemPtr;
                                    ULONG count = width * height;

                                    do {
                                        fputc(data[comp],omm->omm_PGXFiles[comp]);
                                        data += omm->omm_usDepth;
                                    } while(--count);
                                }
                            } else switch(omm->omm_usDepth) {
                            */
                            switch(omm->omm_usDepth) {
                                // Samples per Pixel or Number of Components
                                case 1:
                                case 3: // The direct cases, can write PPM right away.
                                    #ifdef JPG_LIL_ENDIAN
                                        // On those bloddy little endian machines,
                                        // an endian swap is necessary as PNM is
                                        // big-endian.
                                        if (omm->omm_ucPixelType == CTYP_UWORD) {
                                            ULONG count = width * height * omm->omm_usDepth;
                                            UWORD *data = (UWORD *)omm->omm_pMemPtr;

                                            do {
                                                *data = (*data >> 8) | ((*data & 0xff) << 8);
                                                data++;
                                            } while(--count);
                                        }
                                    #endif
                                    //if (omm->omm_ucPixelType == CTYP_UBYTE) {
                                    //    UBYTE *mem = (UBYTE *)(omm->omm_pMemPtr);
                                    //} else if (omm->omm_ucPixelType == CTYP_UWORD) {
                                    //    UWORD *mem = (UWORD *)(omm->omm_pMemPtr);
                                    //} else if (omm->omm_ucPixelType == CTYP_FLOAT) {
                                    //    FLOAT *mem = (FLOAT *)(omm->omm_pMemPtr);
                                    //}
                                    // Write data to target?
                                    // fwrite(
                                    //      ptr; ptr to array of elements to be written
                                    //      size; size in bytes of each element
                                    //      count; number of elements
                                    //      stream: output stream where to be written
                                    // )
                                    //std::cout << "Hmm, should probably write something\n";
                                    // Yup I think this writes the pixel data
                                    ULONG size = omm->omm_ucPixelType & CTYP_SIZE_MASK;
                                    ULONG count = width * height * omm->omm_usDepth;
                                    std::cout << "Size " << size << " count " << count << std::endl;
                                    // For each element
                                    UBYTE *mem = (UBYTE *)(omm->omm_pMemPtr);
                                    std::cout << *mem << std::endl;
                                    //int total_write = 0;
                                    for (int ii = 0; ii < count; ii++) {
                                        // For each byte of the element
                                        for (int jj = 0; jj < size; jj++) {
                                            // Write the byte value to the output
                                            //std::cout << omm->omm_pMemPtr << std::endl;
                                            *oArray = *mem; //omm->omm_pMemPtr;
                                            oArray++;
                                            out->position += 1;
                                            mem++;
                                            //total_write += 1;
                                    //        omm->omm_pMemPtr++;
                                        }
                                        //std::cout << total_write << std::endl;
                                        //std::cout << size * ii + count << std::endl;
                                    }
                                    std::cout << "Written " << size * count << " now at " << out->position << std::endl;
                                    // fwrite(
                                    //    bmm->bmm_pMemPtr,
                                    //    bmm->bmm_ucPixelType & CTYP_SIZE_MASK,
                                    //    width * height * bmm->bmm_usDepth,
                                    //    bmm->bmm_pTarget
                                    // );
                                    break;
                            }
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
