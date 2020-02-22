Configuration (may not be necessary):
```bash

cd pylibjpeg/src/libjpeg
./configure
```
Then open `pylibjpeg/src/libjpeg/automake` and copy the arguments from
``ADDOPTS`` into `extra_compile_args` in `setup.py`. Then:

To compile:
```bash
cd ../../../
python setup.py build_ext --inplace
```

To test working:
```bash
pylibjpeg/scripts/test.py
```
Will create an uncompressed version of `in.jpg` called  `out.pnm` in the
scripts directory. It's a bit dark, open it in ImageJ. Should look like a
transverse MR of a leg.


Tasks
-----

1. ~Modify `Decode()` so it works with an input bytestream instead of a path to
   a file.~ Done! Input numpy array which is probably better.
2. Modify `Decode()` so it outputs to a bytestream rather than a file.
3. Modify `Decode()` so it outputs binary rather than PNM.
4. Modify `Decode()` so it outputs to a numpy array.
5. Implement pixel data handler for *pydicom* and add test coverage.
