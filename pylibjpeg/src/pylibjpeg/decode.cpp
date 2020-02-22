
// Includes
#include "std/stdio.hpp"
#include "std/string.hpp"

#include "decode.hpp"
#include "streamhook.hpp"

#include "../libjpeg/cmd/reconstruct.hpp"
#include "../libjpeg/cmd/bitmaphook.hpp"
#include "../libjpeg/tools/environment.hpp"
#include "../libjpeg/tools/traits.hpp"
#include "../libjpeg/interface/types.hpp"
#include "../libjpeg/interface/hooks.hpp"
#include "../libjpeg/interface/tagitem.hpp"
#include "../libjpeg/interface/parameters.hpp"
#include "../libjpeg/interface/jpeg.hpp"


void Decode(char *inArray, char *outArray, int inLength, int outLength)
{
    /*

    Parameters
    ----------
    char *inArray
        Pointer to the first element of a numpy.ndarray containing the JPEG
        data to be decompressed.
    char *outArray
        Pointer to the first element of a numpy.ndarray where the decompressed
        JPEG data should be written.
    int inLength
        Length of the input array
    int outLength
        Expected length of the output array

    */

    int colortrafo = 1;
    // No alpha channel
    const char *alpha = NULL;
    bool upsample = true;

    // Create a struct with for the input data so we can track its info
    StreamData in = {
        inArray, 0, inLength, &inArray[0], &inArray[inLength - 1]
    };
    StreamData out = {
        outArray, 0, outLength, &outArray[0], &outArray[outLength -1]
    };

    // Our custom hook handler
    struct JPG_Hook streamhook(IStreamHook, &in);
    // JPEG representation from main library interface
    class JPEG *jpeg = JPEG::Construct(NULL);

    if (jpeg) {
        int ok = 1;

        struct JPG_TagItem tags[] = {
            JPG_PointerTag(JPGTAG_HOOK_IOHOOK, &streamhook),
            JPG_PointerTag(JPGTAG_HOOK_IOSTREAM, in.pData),
            #ifdef TEST_MARKER_INJECTION
                // Stop after the image header...
                JPG_ValueTag(
                    JPGTAG_DECODER_STOP, JPGFLAG_DECODER_STOP_FRAME
                ),
            #endif
            JPG_EndTag
        };

        #ifdef TEST_MARKER_INJECTION
            LONG marker;

            // Check whether this is a marker we care about. Note that
            // due to the stop-flag the code aborts within each marker in
            // the main header.
            do {
                // First read the header, or the next part of it.
                ok = jpeg->Read(tags);
                // Get the next marker that could be potentially of some
                // interest for this code.
                marker = jpeg->PeekMarker(NULL);
                if (marker == 0xffe9) {
                    UBYTE buffer[4]; // For the marker and the size.
                    ok = (
                        jpeg->ReadMarker(buffer, sizeof(buffer), NULL) == sizeof(buffer)
                    );

                    if (ok) {
                        int markersize = (buffer[2] << 8) + buffer[3];
                        // This should better be >= 2!
                        if (markersize < 2) {
                            ok = 0;
                        } else {
                            ok = (
                                jpeg->SkipMarker(markersize - 2, NULL) != -1
                            );
                        }
                    }
                }

                // Abort when we hit an essential marker that ends the
                // tables/misc section.
            } while(marker && marker != -1L && ok);

            // Ok, we found the first frame header, do not go for other
            // tables at all, and disable now the stop-flag
            tags->SetTagData(JPGTAG_DECODER_STOP, 0);
        #endif

        // Reads the data and stores various parameters in a struct
        if (ok && jpeg->Read(tags)) {
            UBYTE subx[4], suby[4];
            struct JPG_TagItem atags[] = {
                JPG_ValueTag(JPGTAG_IMAGE_PRECISION, 0),
                JPG_ValueTag(JPGTAG_IMAGE_IS_FLOAT, false),
                JPG_ValueTag(JPGTAG_IMAGE_OUTPUT_CONVERSION, true),
                JPG_EndTag
            };
            struct JPG_TagItem itags[] = {
                JPG_ValueTag(JPGTAG_IMAGE_WIDTH, 0),
                JPG_ValueTag(JPGTAG_IMAGE_HEIGHT, 0),
                JPG_ValueTag(JPGTAG_IMAGE_DEPTH, 0),
                JPG_ValueTag(JPGTAG_IMAGE_PRECISION, 0),
                JPG_ValueTag(JPGTAG_IMAGE_IS_FLOAT, false),
                JPG_ValueTag(JPGTAG_IMAGE_OUTPUT_CONVERSION, true),
                JPG_ValueTag(JPGTAG_ALPHA_MODE, JPGFLAG_ALPHA_OPAQUE),
                JPG_PointerTag(JPGTAG_ALPHA_TAGLIST, atags),
                JPG_PointerTag(JPGTAG_IMAGE_SUBX, subx),
                JPG_PointerTag(JPGTAG_IMAGE_SUBY, suby),
                JPG_ValueTag(JPGTAG_IMAGE_SUBLENGTH, 4),
                JPG_EndTag
            };

            if (jpeg->GetInformation(itags)) {
                ULONG width  = itags->GetTagData(JPGTAG_IMAGE_WIDTH);
                ULONG height = itags->GetTagData(JPGTAG_IMAGE_HEIGHT);
                UBYTE depth  = itags->GetTagData(JPGTAG_IMAGE_DEPTH);
                UBYTE prec   = itags->GetTagData(JPGTAG_IMAGE_PRECISION);
                UBYTE aprec  = 0;
                bool pfm     = itags->GetTagData(JPGTAG_IMAGE_IS_FLOAT)?true:false;
                bool convert = itags->GetTagData(JPGTAG_IMAGE_OUTPUT_CONVERSION)?true:false;
                bool doalpha = itags->GetTagData(JPGTAG_ALPHA_MODE, JPGFLAG_ALPHA_OPAQUE)?true:false;
                bool apfm    = false;
                bool aconvert= false;
                bool writepgx= false;

                if (alpha && doalpha) {
                    aprec    = atags->GetTagData(JPGTAG_IMAGE_PRECISION);
                    apfm     = atags->GetTagData(JPGTAG_IMAGE_IS_FLOAT)?true:false;
                    aconvert = atags->GetTagData(JPGTAG_IMAGE_OUTPUT_CONVERSION)?true:false;
                } else {
                    doalpha  = false; // alpha channel is ignored.
                }

                UBYTE bytesperpixel = sizeof(UBYTE);
                UBYTE pixeltype     = CTYP_UBYTE;
                if (prec > 8) {
                    bytesperpixel = sizeof(UWORD);
                    pixeltype     = CTYP_UWORD;
                }
                if (pfm && convert == false) {
                    bytesperpixel = sizeof(FLOAT);
                    pixeltype     = CTYP_FLOAT;
                }

                UBYTE alphabytesperpixel = sizeof(UBYTE);
                UBYTE alphapixeltype     = CTYP_UBYTE;
                if (aprec > 8) {
                    alphabytesperpixel = sizeof(UWORD);
                    alphapixeltype     = CTYP_UWORD;
                }
                if (apfm && aconvert == false) {
                    alphabytesperpixel = sizeof(FLOAT);
                    alphapixeltype     = CTYP_FLOAT;
                }

                // Alpha channel memory allocation
                UBYTE *amem = NULL;
                // Output data memory allocation
                UBYTE *mem = (UBYTE *)malloc(width * 8 * depth * bytesperpixel);
                if (doalpha)
                    // only one component!
                    amem = (UBYTE *)malloc(width * 8 * alphabytesperpixel);

                if (mem) {
                    // I think the struct here is used to pass parameters to
                    // the writer hook - BitmapHook
                    // We could probably vastly simplify it?
                    struct StreamMemory omm;
                    omm.omm_pMemPtr      = mem;
                    omm.omm_pAlphaPtr    = amem;
                    omm.omm_ulWidth      = width;
                    omm.omm_ulHeight     = height;
                    omm.omm_usDepth      = depth;
                    omm.omm_ucPixelType  = pixeltype;
                    omm.omm_ucAlphaType  = alphapixeltype;
                    //omm.omm_pTarget      = fopen(outfile, "wb");
                    omm.omm_pTarget      = &out;
                    omm.omm_pAlphaTarget = (doalpha)?(fopen(alpha, "wb")):NULL;
                    omm.omm_pSource      = NULL;
                    omm.omm_pAlphaSource = NULL;
                    omm.omm_pLDRSource   = NULL;
                    omm.omm_bFloat       = pfm;
                    omm.omm_bAlphaFloat  = apfm;
                    omm.omm_bBigEndian   = true;
                    omm.omm_bAlphaBigEndian          = true;
                    omm.omm_bNoOutputConversion      = !convert;
                    omm.omm_bNoAlphaOutputConversion = !aconvert;
                    omm.omm_bUpsampling  = upsample;

                    // If upsampling is enabled, the subsampling factors are
                    // all implicitly 1.
                    if (upsample) {
                        memset(subx, 1, sizeof(subx));
                        memset(suby, 1, sizeof(suby));
                    }

                    if (omm.omm_pTarget) {
                        struct JPG_Hook outhook(OStreamHook, &omm);
                        // TODO: implement writing to numpy
                        struct JPG_Hook alphahook(AlphaHook, &omm);

                        // Write the data
                        if (true) {
                            // Just as a demo, run a stripe-based
                            // reconstruction.
                            ULONG y = 0;
                            ULONG lastline;
                            struct JPG_TagItem tags[] = {
                                JPG_PointerTag(JPGTAG_BIH_HOOK, &outhook),
                                JPG_PointerTag(JPGTAG_BIH_ALPHAHOOK, &alphahook),
                                JPG_ValueTag(JPGTAG_DECODER_MINY, y),
                                JPG_ValueTag(JPGTAG_DECODER_MAXY, y + 7),
                                JPG_ValueTag(JPGTAG_DECODER_UPSAMPLE, upsample),
                                JPG_ValueTag(JPGTAG_MATRIX_LTRAFO, colortrafo),
                                JPG_EndTag
                            };

                            // Writes the image data to file somehow
                            // Need to modify to write to ndarray instead
                            //
                            // Reconstruct now the buffered image, line by
                            // line. Could also reconstruct the image as a
                            // whole. What we have here is just a demo
                            // that is not necessarily the most efficient
                            // way of handling images.
                            do {
                                lastline = height;
                                if (lastline > y + 8)
                                    lastline = y + 8;

                                tags[2].ti_Data.ti_lData = y;
                                tags[3].ti_Data.ti_lData = lastline - 1;
                                ok = jpeg->DisplayRectangle(tags);
                                y  = lastline;
                            } while(y < height && ok);
                        }
                    } else {
                        perror("failed to open the output file");
                    }

                    if (omm.omm_pAlphaTarget)
                        fclose(omm.omm_pAlphaTarget);

                    if (amem)
                        free(amem);

                    free(mem);
                } else {
                    fprintf(
                        stderr,
                        "unable to allocate memory to buffer the image"
                    );
                }
            } else ok = 0;
        } else ok = 0;

        if (!ok) {
            const char *error;
            int code = jpeg->LastError(error);
            fprintf(
                stderr,
                "reading a JPEG file failed - error %d - %s\n",
                code,
                error
            );
        }
        JPEG::Destruct(jpeg);
    } else {
        fprintf(stderr, "failed to construct the JPEG object");
    }
}
