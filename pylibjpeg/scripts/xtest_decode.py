#!/usr/bin/env python

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

from pydicom import dcmread
from pydicom.encaps import defragment_data
from pydicom.pixel_data_handlers.util import (
    get_expected_length, reshape_pixel_array, pixel_dtype
)
from pydicom.jpeg import jpgread

from pylibjpeg import decode
from pylibjpeg.data.manager import DATA_DIR


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":
    # OK
    #dsfile = os.path.join(SCRIPT_DIR, 'JPGLosslessP14SV1_1s_1f_8b.dcm')
    # OK
    #dsfile = os.path.join(SCRIPT_DIR, 'JPGLS_1s_1f_16b.dcm')
    # OK
    #dsfile = os.path.join(SCRIPT_DIR, 'JPGExtended.dcm')
    # Fails - bad JPEG; should have SOS:Se of 63 if actually sequential DCT
    #dsfile = os.path.join(SCRIPT_DIR, 'JPEG-lossy.dcm')
    # OK
    #dsfile = os.path.join(SCRIPT_DIR, 'JPGBaseline_3s_1f_8b.dcm')
    #dsfile = os.path.join(DATA_DIR, 'ds', 'JPGExtended_BAD.dcm')
    with open(os.path.join(SCRIPT_DIR, 'temp.jpg'), 'rb') as fp:
        jpg = jpgread(fp)
        print(jpg)
        print(jpg.uid)
        sys.exit()

    ds = dcmread(dsfile)

    print(ds.file_meta['TransferSyntaxUID'])
    keywords = [
        'NumberOfFrames', 'BitsAllocated', 'BitsStored', 'SamplesPerPixel',
        'PixelRepresentation', 'Rows', 'Columns',
        'PhotometricInterpretation', 'PlanarConfiguration'
    ]
    for kw in keywords:
        if kw in ds: print(ds[kw])

    if 'JPEG' not in ds.file_meta.TransferSyntaxUID.name:
        sys.exit('Not a supported Transfer Syntax')

    if getattr(ds, 'NumberOfFrames', 1) > 1:
        sys.exit('Number of Frames > 1 not supported')

    pixel_data = defragment_data(ds.PixelData)

    #fname = os.path.join(SCRIPT_DIR, 'in.jpg')
    #with open(fname, 'wb') as out:
    #    out.write(pixel_data)

    #with open(fname, 'rb') as fp:
    #    jpg = jpgread(fp)
    #    print(jpg)

    #infile = bytes(fname, 'utf-8')
    #outfile = bytes(os.path.join(SCRIPT_DIR, 'out.pnm'), 'utf-8')

    #print(
    #    'Expected length of pixel data in bytes: {}'
    #    .format(get_expected_length(ds))
    #)
    expected_length = ds.Rows * ds.Columns * ds.SamplesPerPixel * (ds.BitsAllocated // 8)

    arr = np.frombuffer(pixel_data, dtype=np.uint8)
    #print(expected_length)
    out = decode(arr, expected_length).view(pixel_dtype(ds))
    print(out.shape, out, out.dtype)
    out = reshape_pixel_array(ds, out)
    #print(out.shape, out)

    plt.imshow(out)
    plt.show()
