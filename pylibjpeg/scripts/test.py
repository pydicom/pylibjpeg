#!/usr/bin/env python

import os
import sys

import numpy as np

from pydicom import dcmread
from pydicom.encaps import defragment_data
from pydicom.pixel_data_handlers.util import get_expected_length
#from pydicom.jpeg import jpgread

from pylibjpeg import decode


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":
    # OK
    #dsfile = os.path.join(SCRIPT_DIR, 'JPGLosslessP14SV1_1s_1f_8b.dcm')
    # OK
    #dsfile = os.path.join(SCRIPT_DIR, 'JPGLS_1s_1f_16b.dcm')
    # Fails - bad JPEG; should have SOS:Se of 63 if actually sequential DCT
    #dsfile = os.path.join(SCRIPT_DIR, 'JPGExtended_1s_1f_12b.dcm')
    # OK
    dsfile = os.path.join(SCRIPT_DIR, 'JPGBaseline_3s_1f_8b.dcm')
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

    fname = os.path.join(SCRIPT_DIR, 'in.jpg')
    with open(fname, 'wb') as out:
        out.write(pixel_data)

    #with open(fname, 'rb') as fp:
    #    jpg = jpgread(fp)
    #    print(jpg)

    #infile = bytes(fname, 'utf-8')
    outfile = bytes(os.path.join(SCRIPT_DIR, 'out.pnm'), 'utf-8')

    print(
        'Expected length of pixel data in bytes: {}'
        .format(get_expected_length(ds))
    )

    arr = np.frombuffer(pixel_data, dtype=np.uint8)
    out = decode(arr, outfile, get_expected_length(ds))

    print(out.shape, out)
