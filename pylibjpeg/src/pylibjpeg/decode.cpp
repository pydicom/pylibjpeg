
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


void Decode(char *inArray, const char *outArray, int inLength, int outLength)
{
    /*

    Parameters
    ----------
    const char *inArray
        Pointer to the first element of a numpy.ndarray containing the JPEG
        data to be decompressed.
    const char *outArray
        Pointer to the first element of a numpy.ndarray where the decompressed
        JPEG data should be written.
    int inLength
        Length of the input array
    int outLength
        Expected length of the output array

    */

    // Values from cmd/main.cpp - can probably hardcode these later
    int colortrafo = 1;
    const char *alpha = NULL;
    bool upsample = true;

    // Create a struct with for the input data so we can track its info
    StreamData in = {
        inArray, 0, 0, inLength, &inArray[0], &inArray[inLength - 1]
    };

    // Our custom hook handler
    struct JPG_Hook streamhook(StreamHook, &in);
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
                    struct BitmapMemory bmm;
                    bmm.bmm_pMemPtr      = mem;
                    bmm.bmm_pAlphaPtr    = amem;
                    bmm.bmm_ulWidth      = width;
                    bmm.bmm_ulHeight     = height;
                    bmm.bmm_usDepth      = depth;
                    bmm.bmm_ucPixelType  = pixeltype;
                    bmm.bmm_ucAlphaType  = alphapixeltype;
                    bmm.bmm_pTarget      = fopen(outfile, "wb");
                    //bmm.bmm_pTarget      = outfile;
                    bmm.bmm_pAlphaTarget = (doalpha)?(fopen(alpha, "wb")):NULL;
                    bmm.bmm_pSource      = NULL;
                    bmm.bmm_pAlphaSource = NULL;
                    bmm.bmm_pLDRSource   = NULL;
                    bmm.bmm_bFloat       = pfm;
                    bmm.bmm_bAlphaFloat  = apfm;
                    bmm.bmm_bBigEndian   = true;
                    bmm.bmm_bAlphaBigEndian          = true;
                    bmm.bmm_bNoOutputConversion      = !convert;
                    bmm.bmm_bNoAlphaOutputConversion = !aconvert;
                    bmm.bmm_bUpsampling  = upsample;

                    memset(bmm.bmm_PGXFiles, 0, sizeof(bmm.bmm_PGXFiles));

                    /*
                    if (depth != 1 && depth != 3)
                        writepgx = true;

                    if (!upsample)
                        writepgx = true;
                    */

                    // If upsampling is enabled, the subsampling factors are
                    // all implicitly 1.
                    if (upsample) {
                        memset(subx, 1, sizeof(subx));
                        memset(suby, 1, sizeof(suby));
                    }


                    bmm.bmm_bWritePGX = writepgx;
                    /*
                    if (writepgx) {
                        for(int i = 0;i < depth;i++) {
                            char headername[256], rawname[256];
                            FILE *hdr;
                            sprintf(headername, "%s_%d.h", outfile,i);
                            sprintf(rawname, "%s_%d.raw", outfile,i);
                            fprintf(bmm.bmm_pTarget, "%s\n", rawname);
                            hdr = fopen(headername, "wb");
                            // FIXME: component dimensions have to differ
                            // without subsampling expansion
                            if (hdr) {
                                fprintf(
                                    hdr,
                                    "P%c ML +%d %d %d\n",
                                    pfm?'F':'G',
                                    prec,
                                    (width  + subx[i] - 1) / subx[i],
                                    (height + suby[i] - 1) / suby[i]
                                );
                                fclose(hdr);
                            }
                            bmm.bmm_PGXFiles[i] = fopen(rawname, "wb");
                        }
                    }
                    */

                    if (bmm.bmm_pTarget) {
                        struct JPG_Hook bmhook(BitmapHook, &bmm);
                        struct JPG_Hook alphahook(AlphaHook, &bmm);
                        // pgx reconstruction is component by component since
                        // we cannot interleave non-upsampled components of differing
                        // subsampling factors.
                        /*
                        if (writepgx) {
                            int comp;
                            for(comp = 0;comp < depth;comp++) {
                                ULONG y = 0;
                                ULONG lastline;
                                ULONG thisheight = height;
                                struct JPG_TagItem tags[] = {
                                    JPG_PointerTag(JPGTAG_BIH_HOOK,&bmhook),
                                    JPG_PointerTag(JPGTAG_BIH_ALPHAHOOK,&alphahook),
                                    JPG_ValueTag(JPGTAG_DECODER_MINY,y),
                                    JPG_ValueTag(JPGTAG_DECODER_MAXY,y + (suby[comp] << 3) - 1),
                                    JPG_ValueTag(JPGTAG_DECODER_UPSAMPLE,upsample),
                                    JPG_ValueTag(JPGTAG_MATRIX_LTRAFO,colortrafo),
                                    JPG_ValueTag(JPGTAG_DECODER_MINCOMPONENT,comp),
                                    JPG_ValueTag(JPGTAG_DECODER_MAXCOMPONENT,comp),
                                    JPG_EndTag
                                };

                                // Reconstruct now the buffered image, line by line. Could also
                                // reconstruct the image as a whole. What we have here is just a demo
                                // that is not necessarily the most efficient way of handling images.
                                do {
                                    lastline = height;
                                    if (lastline > y + (suby[comp] << 3))
                                    lastline = y + (suby[comp] << 3);
                                    tags[2].ti_Data.ti_lData = y;
                                    tags[3].ti_Data.ti_lData = lastline - 1;
                                    ok = jpeg->DisplayRectangle(tags);
                                    y  = lastline;
                                } while(y < thisheight && ok);
                            }

                            for(int i = 0;i < depth;i++) {
                                if (bmm.bmm_PGXFiles[i]) {
                                    fclose(bmm.bmm_PGXFiles[i]);
                                }
                            }
                        } else {
                        */
                        // Write the data
                        if (true) {
                            // Just as a demo, run a stripe-based
                            // reconstruction.
                            ULONG y = 0;
                            ULONG lastline;
                            struct JPG_TagItem tags[] = {
                                JPG_PointerTag(JPGTAG_BIH_HOOK, &bmhook),
                                JPG_PointerTag(JPGTAG_BIH_ALPHAHOOK, &alphahook),
                                JPG_ValueTag(JPGTAG_DECODER_MINY, y),
                                JPG_ValueTag(JPGTAG_DECODER_MAXY, y + 7),
                                JPG_ValueTag(JPGTAG_DECODER_UPSAMPLE, upsample),
                                JPG_ValueTag(JPGTAG_MATRIX_LTRAFO, colortrafo),
                                JPG_EndTag
                            };

                            // PNM header data - not needed
                            /*
                            fprintf(
                                bmm.bmm_pTarget,
                                "P%c\n%d %d\n%d\n",
                                (pfm)?((depth > 1)?'F':'f'):((depth > 1)?('6'):('5')),
                                width,
                                height,
                                (pfm)?(1):((1 << prec) - 1)
                            );

                            if (bmm.bmm_pAlphaTarget)
                                fprintf(
                                    bmm.bmm_pAlphaTarget,
                                    "P%c\n%d %d\n%d\n",
                                    (apfm)?('f'):('5'),
                                    width,
                                    height,
                                    (apfm)?(1):((1 << aprec) - 1)
                                );
                            */

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

                    fclose(bmm.bmm_pTarget);

                    if (bmm.bmm_pAlphaTarget)
                        fclose(bmm.bmm_pAlphaTarget);

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
