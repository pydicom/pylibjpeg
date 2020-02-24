#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import sys

from pydicom import dcmread
from pydicom.pixel_data_handlers.util import convert_color_space
from pylibjpeg import add_handler

add_handler()


def setup_argparse():
    parser = argparse.ArgumentParser(
        description="Extract the pixel data from the DICOM dataset",
        usage="imshow.py file"
    )

    # Parameters
    req = parser.add_argument_group('Parameters')
    req.add_argument(
        "file", help="The DICOM dataset to extract pixel data from", type=str
    )
    opts = parser.add_argument_group("Options")
    opts.add_argument(
        "-i", "--index",
        help="For multiframe pixel data, show this frame",
        type=int,
        default=0,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = setup_argparse()

    ds = dcmread(args.file)
    if 'PixelData' not in ds:
        sys.exit("No Pixel Data in input file")

    arr = ds.pixel_array
    if 'YBR' in ds.PhotometricInterpretation:
        print('Converting to RGB')
        arr = convert_color_space(arr, ds.PhotometricInterpretation, 'RGB')

    if getattr(ds, 'NumberOfFrames', 1) > 1:
        plt.imshow(arr[args.index])
    else:
        plt.imshow(arr)

    plt.show()
