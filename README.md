[![codecov](https://codecov.io/gh/pydicom/pylibjpeg/branch/master/graph/badge.svg)](https://codecov.io/gh/pydicom/pylibjpeg)
[![Build Status](https://travis-ci.org/pydicom/pylibjpeg.svg?branch=master)](https://travis-ci.org/pydicom/pylibjpeg)

## pylibjpeg

A Python wrapper for Thomas Richter's
[libjpeg](https://github.com/thorfdbg/libjpeg), with a focus on providing JPEG
support for [pydicom](https://github.com/pydicom/pydicom).


### Installation
#### Installing the development version
```bash
git clone --recurse-submodules https://github.com/pydicom/pylibjpeg
pip install pylibjpeg
```

### Supported JPEG Formats

| ISO/IEC Standard | ITU Equivalent | JPEG Format |
| --- | --- | --- |
| [10918](https://www.iso.org/standard/18902.html) | [T.81](https://www.itu.int/rec/T-REC-T.81/en) | [JPEG](https://jpeg.org/jpeg/index.html)    |
| [14495](https://www.iso.org/standard/22397.html)   | [T.87](https://www.itu.int/rec/T-REC-T.87/en) | [JPEG-LS](https://jpeg.org/jpegls/index.html) |
| [18477](https://www.iso.org/standard/62552.html)   | | [JPEG XT](https://jpeg.org/jpegxt/) |

### Supported Transfer Syntaxes

| UID | Description |
| --- | --- |
| 1.2.840.10008.1.2.4.50 | JPEG Baseline (Process 1) |
| 1.2.840.10008.1.2.4.51 | JPEG Extended (Process 2 and 4) |
| 1.2.840.10008.1.2.4.57 | JPEG Lossless, Non-Hierarchical (Process 14) |
| 1.2.840.10008.1.2.4.70 | JPEG Lossless, Non-Hierarchical, First-Order Prediction (Process 14 [Selection Value 1]) |
| 1.2.840.10008.1.2.4.80 | JPEG-LS Lossless |
| 1.2.840.10008.1.2.4.81 | JPEG-LS Lossy (Near-Lossless) Image Compression |

### Usage
#### With pydicom
Assuming you already have *pydicom* installed:

```python
from pydicom import dcmread
from pydicom.data import get_testdata_file

# Importing the package automatically adds the pixel data handler
import pylibjpeg

# Use pydicom as normal
ds = dcmread(get_testdata_file('JPEG-LL.dcm'))
arr = ds.pixel_array
```

#### Without pydicom

```python
from pylibjpeg import decode

with open('filename.jpg', 'wb') as f:
    # Returns a numpy array
    arr = decode(f.read())
```
