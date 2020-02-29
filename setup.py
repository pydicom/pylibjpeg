
import os
import sys
from pathlib import Path
import platform
import setuptools
from setuptools import setup, find_packages
from setuptools.extension import Extension
import subprocess
import distutils.sysconfig  # conda doesn't like not importing this


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
    # Needs to be run from within the libjpeg directory
    current_dir = os.getcwd()
    fpath = os.path.abspath(LIBJPEG_SRC)
    os.chdir(LIBJPEG_SRC)
    subprocess.call(os.path.join(fpath, 'configure'))
    os.chdir(current_dir)

# Get compilation options
with open(os.path.join(LIBJPEG_SRC, 'automakefile')) as fp:
    lines = fp.readlines()

lines = [ll for ll in lines if not ll.startswith('#')]
opts = [ll.split('=', 1) for ll in lines]
opts = {vv[0].strip():list(vv[1].strip().split(' ')) for vv in opts}

#print('automakefile options')
#for kk, vv in opts.items():
#    print(kk, vv)

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

extra_link_args = []
extra_link_args.extend(opts['EXTRA_LIBS'])

include_dirs = [
    LIBJPEG_SRC,
    PYLIBJPEG_SRC,
    distutils.sysconfig.get_python_inc(),
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

with open('README.md', 'r') as fp:
    long_description = fp.read()

setup(
    name = 'pylibjpeg',
    description = (
        "A Python wrapper for libjpeg, with a focus on JPEG support "
        "for pydicom"
    ),
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    version = __version__,
    author = "scaramallion",
    author_email = "scaramallion@users.noreply.github.com",
    url = "https://github.com/pydicom/pylibjpeg",
    license = "GPL V3.0",
    keywords = (
        "dicom pydicom python medicalimaging radiotherapy oncology imaging "
        "jpeg jpeg-ls"
    ),
    project_urls = {
        # Might give it it's own docs eventually
        'Documentation' : 'https://pydicom.github.io/pydicom/'
    },
    classifiers = [
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
        #"Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: MacOS :: MacOS X",  # Tested OK
        "Operating System :: POSIX :: Linux",  # Tested OK
        "Operating System :: OS Independent",  # In theory...
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries",
    ],
    packages = find_packages(),
    package_data = {'': ['*.txt', '*.cpp', '*.h', '*.hpp', '*.pyx']},
    include_package_data = True,
    zip_safe = False,
    python_requires = ">=3.6",
    setup_requires = ['setuptools>=18.0', 'cython', 'numpy'],
    install_requires = ['cython', "numpy"],
    cmdclass = {'build_ext': my_build_ext},
    ext_modules = [ext],
)
