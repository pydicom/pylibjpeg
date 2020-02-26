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

### Usage

Assuming you already have *pydicom* installed:

```python
from pydicom import dcmread
from pydicom.data import get_testdata_file

from pylibjpeg import add_handler

# Add the pylibjpeg pixel data handler to pydicom
add_handler()

# Use pydicom as normal
ds = dcmread(get_testdata_file('JPEG-LL.dcm'))
arr = ds.pixel_array
```
