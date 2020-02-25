#!/usr/bin/env python

import os
import sys
from tempfile import NamedTemporaryFile

import numpy as np
import matplotlib.pyplot as plt

from pydicom import dcmread
from pydicom.encaps import defragment_data
from pydicom.pixel_data_handlers.util import (
    get_expected_length, reshape_pixel_array, pixel_dtype
)

from pylibjpeg.libjpeg import reconstruct
from pylibjpeg.data.manager import get_datasets


if __name__ == "__main__":
    fname = get_datasets('1.2.840.10008.1.2.4.50')[1]
    ds = dcmread(fname)

    if getattr(ds, 'NumberOfFrames', 1) > 1:
        sys.exit('Number of Frames > 1 not supported')

    pixel_data = defragment_data(ds.PixelData)

    tfin = NamedTemporaryFile('wb')
    tfin.write(pixel_data)
    tfin.seek(0)

    tfout = NamedTemporaryFile('rb+')
    reconstruct(tfin.name, tfout.name)
    tfout.seek(0)

    from io import BytesIO
    data = BytesIO(tfout.read())

    # Needs pillow, write a parser for numpy instead...
    plt.imshow(plt.imread(data, format='PPM'))
    plt.show()
