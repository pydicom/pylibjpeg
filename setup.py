import os
import sys
from pathlib import Path

import numpy as np
import setuptools

from setuptools import setup, find_packages
from setuptools.extension import Extension

from Cython.Distutils import build_ext

LIB_DIR = os.path.abspath(os.path.dirname(__file__))

# Cython extension.
source_files = ['pyjpeg/_jpeg.pyx']
libdir = os.path.join(LIB_DIR, 'pyjpeg/src/libjpeg/')
for fname in Path(libdir).glob('*/*'):
    if '.cpp' in str(fname):
        source_files.append(str(fname))

#print(source_files)

include_dirs = [
    os.path.join(LIB_DIR, 'pyjpeg/src/libjpeg/'),
    setuptools.distutils.sysconfig.get_python_inc(),
    np.get_include()
]

# AUTOCONF is important!
# Steal from automakefile
#ADDOPTS = -DUSE_AUTOCONF -mfpmath=387
#LIB_OPTS = -fvisibility=internal -fPIC -DBUILD_LIB
#EXTRA_LIBS = -lgcc_s
extra_compile_args = ["-DUSE_AUTOCONF", "-mfpmath=387"]
extra_link_args = []


ext = Extension(
    '_jpeg',
    source_files,
    language='c++',
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

setup(
    name='pyjpeg',
    packages=find_packages(),
    package_data={'': ['*.txt', '*.cpp', '*.h', '*.hpp', '*.pyx']},
    cmdclass={'build_ext': build_ext},
    ext_modules = [ext],
    version='0.0.1'
)
