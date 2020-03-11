[![codecov](https://codecov.io/gh/pydicom/pylibjpeg/branch/master/graph/badge.svg)](https://codecov.io/gh/pydicom/pylibjpeg)
[![Build Status](https://travis-ci.org/pydicom/pylibjpeg.svg?branch=master)](https://travis-ci.org/pydicom/pylibjpeg)

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
plugins come in. To support a given JPEG format you first have to install
the corresponding package:

| JPEG Format | Decode | Encode | Plugin | Based on |
|---|------|---|---|---|
| JPEG, JPEG-LS and JPEG XT | Yes | No | [pylibjpeg-libjpeg](https://github.com/pydicom/pylibjpeg-libjpeg) | [libjpeg](https://github.com/thorfdbg/libjpeg) |
| JPEG 2000 | No | No | To be implemented | [openjpeg](https://github.com/uclouvain/openjpeg)|

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
