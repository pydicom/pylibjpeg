[![codecov](https://codecov.io/gh/pydicom/pylibjpeg/branch/master/graph/badge.svg)](https://codecov.io/gh/pydicom/pylibjpeg)
[![Build Status](https://github.com/pydicom/pylibjpeg/workflows/build/badge.svg)](https://github.com/pydicom/pylibjpeg/actions?query=workflow%3Abuild)
[![PyPI version](https://badge.fury.io/py/pylibjpeg.svg)](https://badge.fury.io/py/pylibjpeg)
[![Python versions](https://img.shields.io/pypi/pyversions/pylibjpeg.svg)](https://img.shields.io/pypi/pyversions/pylibjpeg.svg)

## pylibjpeg

A Python 3.7+ framework for decoding JPEG images and decoding/encoding RLE datasets, with a focus on providing support for [pydicom](https://github.com/pydicom/pydicom).


### Installation
#### Installing the current release

```
pip install pylibjpeg
```

##### Installing extra requirements

The package can be installed with extra requirements to enable support for JPEG (with `libjpeg`), JPEG 2000 (with `openjpeg`) and Run-Length Encoding (RLE) (with `rle`), respectively:

```
pip install pylibjpeg[libjpeg,openjpeg,rle]
```

Or alternatively with just `all`:

```
pip install pylibjpeg[all]
```

#### Installing the development version

Make sure [Git](https://git-scm.com/) is installed, then
```bash
git clone https://github.com/pydicom/pylibjpeg
python -m pip install pylibjpeg
```

### Plugins

One or more plugins are required before *pylibjpeg* is able to handle JPEG images or RLE datasets. To handle a given format or DICOM Transfer Syntax
you first have to install the corresponding package:

#### Supported Formats
|Format                   |Decode?|Encode?|Plugin                 |Based on     |
|---                      |------ |---    |---                    |---          |
|JPEG, JPEG-LS and JPEG XT|Yes    |No     |[pylibjpeg-libjpeg][1] |[libjpeg][2] |
|JPEG 2000                |Yes    |No     |[pylibjpeg-openjpeg][3]|[openjpeg][4]|
|RLE Lossless (PackBits)  |Yes    |Yes    |[pylibjpeg-rle][5]     |-            |

#### DICOM Transfer Syntax

|UID                   | Description                                    | Plugin                |
|---                   |---                                             |----                   |
|1.2.840.10008.1.2.4.50|JPEG Baseline (Process 1)                       |[pylibjpeg-libjpeg][1] |
|1.2.840.10008.1.2.4.51|JPEG Extended (Process 2 and 4)                 |[pylibjpeg-libjpeg][1] |
|1.2.840.10008.1.2.4.57|JPEG Lossless, Non-Hierarchical (Process 14)    |[pylibjpeg-libjpeg][1] |
|1.2.840.10008.1.2.4.70|JPEG Lossless, Non-Hierarchical, First-Order Prediction</br>(Process 14, Selection Value 1) | [pylibjpeg-libjpeg][1]|
|1.2.840.10008.1.2.4.80|JPEG-LS Lossless                                |[pylibjpeg-libjpeg][1] |
|1.2.840.10008.1.2.4.81|JPEG-LS Lossy (Near-Lossless) Image Compression |[pylibjpeg-libjpeg][1] |
|1.2.840.10008.1.2.4.90|JPEG 2000 Image Compression (Lossless Only)     |[pylibjpeg-openjpeg][4]|
|1.2.840.10008.1.2.4.91|JPEG 2000 Image Compression                     |[pylibjpeg-openjpeg][4]|
|1.2.840.10008.1.2.5   |RLE Lossless                                    |[pylibjpeg-rle][5]     |

If you're not sure what the dataset's *Transfer Syntax UID* is, it can be
determined with:
```python
>>> from pydicom import dcmread
>>> ds = dcmread('path/to/dicom_file')
>>> ds.file_meta.TransferSyntaxUID.name
```

[1]: https://github.com/pydicom/pylibjpeg-libjpeg
[2]: https://github.com/thorfdbg/libjpeg
[3]: https://github.com/pydicom/pylibjpeg-openjpeg
[4]: https://github.com/uclouvain/openjpeg
[5]: https://github.com/pydicom/pylibjpeg-rle


### Usage
#### Decoding
##### With pydicom
Assuming you have *pydicom* v2.1+ and suitable plugins installed:

```python
from pydicom import dcmread
from pydicom.data import get_testdata_file

# With the pylibjpeg-libjpeg plugin
ds = dcmread(get_testdata_file('JPEG-LL.dcm'))
jpg_arr = ds.pixel_array

# With the pylibjpeg-openjpeg plugin
ds = dcmread(get_testdata_file('JPEG2000.dcm'))
j2k_arr = ds.pixel_array

# With the pylibjpeg-rle plugin and pydicom v2.2+
ds = dcmread(get_testdata_file('OBXXXX1A_rle.dcm'))
# pydicom defaults to the numpy handler for RLE so need
# to explicitly specify the use of pylibjpeg
ds.decompress("pylibjpeg")
rle_arr = ds.pixel_array
```

For datasets with multiple frames you can reduce your memory usage by
processing each frame separately using the ``generate_frames()`` generator
function:
```python
from pydicom import dcmread
from pydicom.data import get_testdata_file
from pydicom.pixel_data_handlers.pylibjpeg_handler import generate_frames

ds = dcmread(get_testdata_file('color3d_jpeg_baseline.dcm'))
frames = generate_frames(ds)
arr = next(frames)
```

##### Standalone JPEG decoding
You can also just use *pylibjpeg* to decode JPEG images to a [numpy ndarray](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html), provided you have a suitable plugin installed:
```python
from pylibjpeg import decode

# Can decode using the path to a JPG file as str or path-like
arr = decode('filename.jpg')

# Or a file-like...
with open('filename.jpg', 'rb') as f:
    arr = decode(f)

# Or bytes...
with open('filename.jpg', 'rb') as f:
    arr  = decode(f.read())
```

#### Encoding
##### With pydicom

Assuming you have *pydicom* v2.2+ and suitable plugins installed:

```python
from pydicom import dcmread
from pydicom.data import get_testdata_file
from pydicom.uid import RLELossless

ds = dcmread(get_testdata_file("CT_small.dcm"))

# Encode in-place using RLE Lossless and update the dataset
# Updates the Pixel Data, Transfer Syntax UID and Planar Configuration
ds.compress(uid)

# Save compressed
ds.save_as("CT_small_rle.dcm")
```
