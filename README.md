## pylibjpeg

A Python wrapper for Thomas Richter's
[libjpeg](https://github.com/thorfdbg/libjpeg) with a focus on providing JPEG
support for [pydicom](https://github.com/pydicom/pydicom).


### Installation

```bash
git clone https://github.com/scaramallion/pylibjpeg
cd pylibjpeg
git submodule update --init --recursive
pip install .
```

### Usage

#### With *pydicom*

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
