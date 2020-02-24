pylibjpeg
---------
A Python wrapper for Thomas Richter's
[libjpeg](https://github.com/thorfdbg/libjpeg), intended
for use with [pydicom](https://github.com/pydicom/pydicom).

Installation
------------

Make take a minute or two to install due to the need to compile ``libjpeg``
```bash
pip install git+https://github.com/scaramallion/pylibjpeg.git
```

Usage
-----
With pydicom
............
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
