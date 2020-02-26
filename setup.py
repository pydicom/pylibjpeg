
import os
import sys
from pathlib import Path
import setuptools
from setuptools import setup, find_packages
from setuptools.extension import Extension
import subprocess


# Workaround for needing cython and numpy
# Solution from: https://stackoverflow.com/a/54138355/12606901
def my_build_ext(args):
    from Cython.Distutils import build_ext as _build_ext

    class build_ext(_build_ext):
        def finalize_options(self):
            _build_ext.finalize_options(self)
            __builtins__.__NUMPY_SETUP__ = False
            import numpy
            self.include_dirs.append(numpy.get_include())

    return build_ext(args)


LIBJPEG_SRC = os.path.join('pylibjpeg', 'src', 'libjpeg')
PYLIBJPEG_SRC = os.path.join('pylibjpeg', 'src', 'pylibjpeg')

# Run configure script once
if 'config.log' not in os.listdir(LIBJPEG_SRC):
    subprocess.call(os.path.join(LIBJPEG_SRC, 'configure'))

# Get compilation options
with open(os.path.join(LIBJPEG_SRC, 'automakefile')) as fp:
    lines = fp.readlines()

lines = [ll for ll in lines if not ll.startswith('#')]
opts = [ll.split('=', 1) for ll in lines]
opts = {vv[0].strip():list(vv[1].strip().split(' ')) for vv in opts}

print('automakefile options')
for kk, vv in opts.items():
    print(kk, vv)

#os.environ["CC"] = opts['COMPILER_CMD'][0]
#os.environ["CXX"] = opts['COMPILER_CMD'][0]

# Cython extension.
source_files = [
    'pylibjpeg/_libjpeg.pyx',
    os.path.join(PYLIBJPEG_SRC, 'decode.cpp'),
    os.path.join(PYLIBJPEG_SRC, 'streamhook.cpp'),
]
for fname in Path(LIBJPEG_SRC).glob('*/*'):
    if '.cpp' in str(fname):
        source_files.append(str(fname))

extra_compile_args = []
extra_compile_args.extend(opts['ADDOPTS'])

# OSX with clang we need -mno-sse to use -mfpmath=387
print(os.environ)
if 'TRAVIS_OS_NAME' in os.environ and os.environ.get('TRAVIS_OS_NAME') == 'osx':
    extra_compile_args.append('-mno-sse')

extra_link_args = []
extra_link_args.extend(opts['EXTRA_LIBS'])

include_dirs = [
    LIBJPEG_SRC,
    PYLIBJPEG_SRC,
    setuptools.distutils.sysconfig.get_python_inc(),
]

ext = Extension(
    '_libjpeg',
    source_files,
    language='c++',
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

VERSION_FILE = os.path.join('pylibjpeg', '_version.py')
with open(VERSION_FILE) as fp:
    exec(fp.read())

setup(
    name='pylibjpeg',
    packages=find_packages(),
    python_requires=">=3.6",
    package_data={'': ['*.txt', '*.cpp', '*.h', '*.hpp', '*.pyx']},
    include_package_data = True,
    version=__version__,
    zip_safe=False,
    setup_requires=['setuptools>=18.0', 'cython', 'numpy'],
    install_requires=['cython', "numpy"],
    cmdclass={'build_ext': my_build_ext},
    ext_modules = [ext],
)
