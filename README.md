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

Roadmap to v1.0
---------------

1. ~Modify `Decode()` so it works with an input bytestream instead of a path to
   a file.~ Done! Input numpy array which is probably better.
2. ~Modify `Decode()` so it outputs to a bytestream rather than a file.~
3. ~Modify `Decode()` so it outputs binary rather than PNM.~
4. ~Modify `Decode()` so it outputs to a numpy array.~
5. ~Cleanup code, add buffer overflow checks, etc.~
6. ~Implement pixel data handler for *pydicom*~ and add test coverage. Need
   more test data...
7. Change `Decode()` to return success/fail so can raise exceptions if needed
8. Make JPEG image details available (precision, size, etc)
9. ~Add interface for the `cmd/Reconstruct()` method to allow regular usage~
10. ~Autoconfigure on install, update compiler options~ not sure how robust
    it is (windows? conda?)...
11. Decode regular JPEG (non-DICOM) to shaped numpy array for non-pydicom
    users (needs \#8)
12. Package housekeeping stuff, Travis, docs, etc.

The Future \*wiggles fingers\*
------------------------------

1. Add support for [openjpeg](https://github.com/uclouvain/openjpeg) library
   and JPEG2K?
