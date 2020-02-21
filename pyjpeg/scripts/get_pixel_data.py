#!/usr/bin/env python

import argparse
import sys

from pydicom import dcmread
from pydicom.encaps import defragment_data, decode_data_sequence


def setup_argparse():
    parser = argparse.ArgumentParser(
        description="Extract the pixel data from the DICOM dataset",
        usage="get_pixel_data.py file"
    )

    # Parameters
    req = parser.add_argument_group('Parameters')
    req.add_argument(
        "file", help="The DICOM dataset to extract pixel data from", type=str
    )
    opts = parser.add_argument_group("Options")
    opts.add_argument(
        "-p",
        help="The prefix to use for the extracted images",
        type=str,
        default="im"
    )
    opts.add_argument(
        "-v",
        help="Print verbose output",
        action="store_true"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = setup_argparse()

    ds = dcmread(args.file)
    if 'PixelData' not in ds:
        sys.exit("No Pixel Data in input file")

    if args.v:
        print(ds.file_meta['TransferSyntaxUID'])
        keywords = [
            'NumberOfFrames', 'BitsAllocated', 'BitsStored', 'SamplesPerPixel',
            'PixelRepresentation', 'Rows', 'Columns',
            'PhotometricInterpretation', 'PlanarConfiguration'
        ]
        for kw in keywords:
            if kw in ds: print(ds[kw])

    ext = 'jpg' if 'JPEG' in ds.file_meta.TransferSyntaxUID.name else 'bin'

    if getattr(ds, 'NumberOfFrames', 1) > 1:
        pixel_data = decode_data_sequence(ds.PixelData)
        for frame, ii in enumerate(frames):
            fname = '{}_{:04d}.{}'.format(args.p, ii, ext)
            with open(fname, 'wb') as out:
                out.write(frame)
    else:
        pixel_data = defragment_data(ds.PixelData)
        fname = '{}.{}'.format(args.p, ext)
        with open(fname, 'wb') as out:
            out.write(pixel_data)
