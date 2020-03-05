
// Includes
#include "std/stdio.hpp"
#include "std/string.hpp"
#include <sstream>

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


std::string Decode(char *inArray, char *outArray, int inLength, int outLength, int colourTransform)
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
    int colourTransform
        JPGFLAG_MATRIX_COLORTRANSFORMATION_NONE 0
        JPGFLAG_MATRIX_COLORTRANSFORMATION_YCBCR 1
        JPGFLAG_MATRIX_COLORTRANSFORMATION_LSRCT 2
        JPGFLAG_MATRIX_COLORTRANSFORMATION_RCT 2
        JPGFLAG_MATRIX_COLORTRANSFORMATION_FREEFORM 3

    */
    // Check valid value
    if (colourTransform < 0 || colourTransform > 3) {
        return "-8194::::Invalid colourTransform value";
    }
    int colortrafo = colourTransform;
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
            JPG_EndTag
        };

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

                // Make sure output array is the correct size
                if (width * height * depth * bytesperpixel != outLength) {
                    return "-8195::::Invalid output array size";
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

                    struct JPG_Hook outhook(OStreamHook, &omm);
                    // TODO: implement writing alpha to numpy
                    // Not required for DICOM
                    struct JPG_Hook alphahook(AlphaHook, &omm);

                    // Write the data
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

                    // Writes the image data to numpy array
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
                        // I think this is the decode/writer line
                        ok = jpeg->DisplayRectangle(tags);
                        y  = lastline;
                    } while(y < height && ok);

                    if (omm.omm_pAlphaTarget)
                        fclose(omm.omm_pAlphaTarget);

                    if (amem)
                        free(amem);

                    free(mem);
                } else {
                    // Unable to allocate memory to buffer the image
                    return "-8192::::Unable to allocate memory to buffer the image";
                }
            } else ok = 0;
        } else ok = 0;

        if (!ok) {
            const char *error;
            int code = jpeg->LastError(error);
            std::ostringstream status;
            status << code << "::::" << error;
            return status.str();
        }
        JPEG::Destruct(jpeg);
    } else {
        // Failed to construct the JPEG object
        return "-8193::::Failed to construct the JPEG object";
    }
    // Success
    return "0::::";
}


std::string GetJPEGParameters(char *inArray, int inLength, struct JPEGParameters *param)
{
    /*

    Parameters
    ----------
    char *inArray
        Pointer to the first element of a numpy.ndarray containing the JPEG
        data to be read.
    int inLength
        Length of the input array

    */

    // Create a struct for the input
    StreamData in = {
        inArray, 0, inLength, &inArray[0], &inArray[inLength - 1]
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
            JPG_EndTag,
        };

        // Reads the data and stores various parameters in a struct
        // Peek marker is useless, returns 0 for most markers
        if (ok && jpeg->Read(tags)) {
            UBYTE subx[4], suby[4];
            struct JPG_TagItem itags[] = {
                JPG_ValueTag(JPGTAG_IMAGE_WIDTH, 0),
                JPG_ValueTag(JPGTAG_IMAGE_HEIGHT, 0),
                JPG_ValueTag(JPGTAG_IMAGE_DEPTH, 0),
                JPG_ValueTag(JPGTAG_IMAGE_PRECISION, 0),
                JPG_ValueTag(JPGTAG_IMAGE_IS_FLOAT, false),
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

                param->columns = width;
                param->rows = height;
                param->samples_per_pixel = depth;
                param->bits_per_sample = prec;
            } else ok = 0;
        } else ok = 0;

        if (!ok) {
            const char *error;
            int code = jpeg->LastError(error);
            std::ostringstream status;
            status << code << "::::" << error;
            return status.str();
        }
        JPEG::Destruct(jpeg);
    } else {
        // Failed to construct the JPEG object
        return "-8193::::Failed to construct the JPEG object";
    }
    // Success
    return "0::::";
}
