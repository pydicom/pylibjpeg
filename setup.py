
import os
import sys
from pathlib import Path
import setuptools
from setuptools import setup, find_packages
from setuptools.extension import Extension
import subprocess

# Install dependencies required by setup.py
from pip._internal import main as pip
pip(['install', 'numpy', 'cython'])

# Dependencies
import numpy as np
from Cython.Distutils import build_ext

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

os.environ["CC"] = opts['COMPILER_CMD'][0]
os.environ["CXX"] = opts['COMPILER_CMD'][0]

# Cython extension.
source_files = [
    'pylibjpeg/_libjpeg.pyx',
    os.path.join(PYLIBJPEG_SRC, 'decode.cpp'),
    os.path.join(PYLIBJPEG_SRC, 'streamhook.cpp'),
]
for fname in Path(LIBJPEG_SRC).glob('*/*'):
    if '.cpp' in str(fname):
        source_files.append(str(fname))

#print('Source files:')
#for src in source_files:
#    print(' ', src)

include_dirs = [
    LIBJPEG_SRC,
    PYLIBJPEG_SRC,
    setuptools.distutils.sysconfig.get_python_inc(),
    np.get_include(),
]

extra_compile_args = []
extra_compile_args.extend(opts['ADDOPTS'])
# Hmm, don't use -DBUILD_LIB
#extra_compile_args.extend(opts['LIB_OPTS'])
extra_link_args = []
extra_link_args.extend(opts['EXTRA_LIBS'])

#print(extra_compile_args)
#print(extra_link_args)

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
    cmdclass={'build_ext': build_ext},
    ext_modules = [ext],
    include_package_data = True,
    version=__version__,
    zip_safe=False,
    #setup_requires=['cython', 'numpy'],
    install_requires=["numpy"],
)
