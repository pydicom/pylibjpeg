import os
import sys
from pathlib import Path

import numpy as np
import setuptools

from setuptools import setup, find_packages
from setuptools.extension import Extension

from Cython.Distutils import build_ext

PACKAGE_DIR = os.path.abspath(os.path.dirname(__file__))
LIBJPEG_SRC = os.path.join(PACKAGE_DIR, 'pylibjpeg', 'src', 'libjpeg')
PYLIBJPEG_SRC = os.path.join(PACKAGE_DIR, 'pylibjpeg', 'src', 'pylibjpeg')

# Cython extension.
source_files = [
    'pylibjpeg/_libjpeg.pyx',
    # For decode()
    os.path.join(PYLIBJPEG_SRC, 'decode.cpp'),
    os.path.join(PYLIBJPEG_SRC, 'streamhook.cpp'),
    #os.path.join(LIBJPEG_SRC, 'cmd/reconstruct.cpp'),
]
for fname in Path(LIBJPEG_SRC).glob('*/*'):
    if '.cpp' in str(fname):
        source_files.append(str(fname))

#print(source_files)

include_dirs = [
    LIBJPEG_SRC,
    PYLIBJPEG_SRC,
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
    '_libjpeg',
    source_files,
    language='c++',
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

setup(
    name='pylibjpeg',
    packages=find_packages(),
    package_data={'': ['*.txt', '*.cpp', '*.h', '*.hpp', '*.pyx']},
    cmdclass={'build_ext': build_ext},
    ext_modules = [ext],
    version='0.0.1'
)
