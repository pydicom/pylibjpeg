[![codecov](https://codecov.io/gh/pydicom/pylibjpeg/branch/master/graph/badge.svg)](https://codecov.io/gh/pydicom/pylibjpeg)
[![Build Status](https://travis-ci.org/pydicom/pylibjpeg.svg?branch=master)](https://travis-ci.org/pydicom/pylibjpeg)
[![PyPI version](https://badge.fury.io/py/pylibjpeg.svg)](https://badge.fury.io/py/pylibjpeg)
[![Python versions](https://img.shields.io/pypi/pyversions/pylibjpeg.svg)](https://img.shields.io/pypi/pyversions/pylibjpeg.svg)

## pylibjpeg

A Python 3.6+ framework for decoding JPEG images, with a focus on providing JPEG support for [pydicom](https://github.com/pydicom/pydicom).


### Installation
#### Installing the current release

```
pip install pylibjpeg
```

#### Installing the development version

Make sure [Git](https://git-scm.com/) is installed, then
```bash
git clone https://github.com/pydicom/pylibjpeg
python -m pip install pylibjpeg
```

### Plugins

By itself *pylibjpeg* is unable to decode any JPEG images, which is where the
plugins come in. To support a given JPEG format or DICOM Transfer Syntax
you first have to install the corresponding package:

#### JPEG Format
| Format | Decode? | Encode? | Plugin | Based on |
|---|------|---|---|---|
| JPEG, JPEG-LS and JPEG XT | Yes | No | [pylibjpeg-libjpeg][1] | [libjpeg][2] |

#### Transfer Syntax

| UID | Description | Plugin |
|---|---|----|
| 1.2.840.10008.1.2.4.50 | JPEG Baseline (Process 1) | [pylibjpeg-libjpeg][1] |
| 1.2.840.10008.1.2.4.51 | JPEG Extended (Process 2 and 4) | [pylibjpeg-libjpeg][1]|
| 1.2.840.10008.1.2.4.57 | JPEG Lossless, Non-Hierarchical (Process 14) | [pylibjpeg-libjpeg][1]|
| 1.2.840.10008.1.2.4.70 | JPEG Lossless, Non-Hierarchical, First-Order Prediction</br>(Process 14, Selection Value 1) | [pylibjpeg-libjpeg][1]|
| 1.2.840.10008.1.2.4.80 | JPEG-LS Lossless | [pylibjpeg-libjpeg][1]|
| 1.2.840.10008.1.2.4.81 | JPEG-LS Lossy (Near-Lossless) Image Compression | [pylibjpeg-libjpeg][1]|
| 1.2.840.10008.1.2.4.90 | JPEG 2000 Image Compression (Lossless Only) | Not yet supported |
| 1.2.840.10008.1.2.4.91 | JPEG 2000 Image Compression | Not yet supported |

If you're not sure what the dataset's *Transfer Syntax UID* is, it can be
determined with:
```python
>>> from pydicom import dcmread
>>> ds = dcmread('path/to/dicom_file')
>>> ds.file_meta.TransferSyntaxUID.name
```

[1]: https://github.com/pydicom/pylibjpeg-libjpeg
[2]: https://github.com/thorfdbg/libjpeg


### Usage
#### With pydicom
Assuming you already have *pydicom* v1.4+ installed:

```python
from pydicom import dcmread
from pydicom.data import get_testdata_file

# With the pylibjpeg-libjpeg plugin installed
import pylibjpeg

ds = dcmread(get_testdata_file('JPEG-LL.dcm'))
arr = ds.pixel_array
```

For datasets with multiple frames you can reduce your memory usage by
processing each frame separately using the ``generate_frames()`` generator
function:
```python
from pydicom import dcmread
from pydicom.data import get_testdata_file

from pylibjpeg import generate_frames

ds = dcmread(get_testdata_file('color3d_jpeg_baseline.dcm'))
frames = generate_frames(ds)
arr = next(frames)
```

#### Standalone JPEG decoding
You can also just use *pylibjpeg* to decode JPEG images to a [numpy ndarray](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html), provided you have a suitable plugin installed:
```python
from pylibjpeg import decode

# Can decode using the path to a JPG file as str or pathlike
arr = decode('filename.jpg')

# Or a file-like...
with open('filename.jpg', 'rb') as f:
    arr = decode(f)

# Or bytes...
with open('filename.jpg', 'rb') as f:
    arr  = decode(f.read())
```
