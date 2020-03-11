[![codecov](https://codecov.io/gh/pydicom/pylibjpeg/branch/master/graph/badge.svg)](https://codecov.io/gh/pydicom/pylibjpeg)
[![Build Status](https://travis-ci.org/pydicom/pylibjpeg.svg?branch=master)](https://travis-ci.org/pydicom/pylibjpeg)

## pylibjpeg

A Python 3.6+ framework for decoding JPEG images, with a focus on providing
support for [pydicom](https://github.com/pydicom/pydicom).

Linux, OSX and Windows are all supported.


### Installation
#### Installing the development version

Make sure [Python](https://www.python.org/) and [Git](https://git-scm.com/) are installed.
```bash
git clone https://github.com/pydicom/pylibjpeg
python -m pip install pylibjpeg
```

### Plugins

By itself *pylibjpeg* is unable to decode any JPEG images, which is where the
plugins come in. To support the given JPEG format you'll first have to install
the corresponding package:

* JPEG, JPEG-LS and JPEG XT: [pylibjpeg-libjpeg](https://github.com/pydicom/pylibjpeg-libjpeg)
* JPEG2000: To be implemented

### Usage
#### With pydicom
Assuming you already have *pydicom* installed:

```python
from pydicom import dcmread
from pydicom.data import get_testdata_file

# With the pylibjpeg-libjpeg plugin
import pylibjpeg

ds = dcmread(get_testdata_file('JPEG-LL.dcm'))
arr = ds.pixel_array
```

#### Standalone

```python
from pylibjpeg import decode

with open('filename.jpg', 'rb') as f:
    # Returns a numpy array
    arr = decode(f.read())
```
