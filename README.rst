To get running for testing:
```bash
cd pyjpeg/src/
git clone --depth=1 https://github.com/thorfdbg/libjpeg
cd libjpeg
./configure
```
Then open `pyjpeg/src/libjpeg/automake` and copy the arguments from
``ADDOPTS`` into `extra_compile_args` in `setup.py`. Then:
```bash
cd ../../../
python setup.py build_ext --inplace
pyjpeg/scripts/test.py
```
Will create an uncompressed version of `in.jpg` called  `out.pnm` in the
scripts directory. It's a bit dark, open it in ImageJ.
