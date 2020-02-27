[![codecov](https://codecov.io/gh/scaramallion/pylibjpeg/branch/master/graph/badge.svg)](https://codecov.io/gh/scaramallion/pylibjpeg)
[![Build Status](https://travis-ci.org/scaramallion/pylibjpeg.svg?branch=master)](https://travis-ci.org/scaramallion/pylibjpeg)

## pylibjpeg

A Python wrapper for Thomas Richter's
[libjpeg](https://github.com/thorfdbg/libjpeg) with a focus on providing JPEG
support for [pydicom](https://github.com/pydicom/pydicom).


### Installation
#### Installing the development version
```bash
git clone --recurse-submodules https://github.com/scaramallion/pylibjpeg
pip install pylibjpeg
```

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
