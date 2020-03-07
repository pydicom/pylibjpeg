
import os
import sys
from pathlib import Path
import platform
import setuptools
from setuptools import setup, find_packages
from setuptools.extension import Extension
import subprocess
from distutils.command.build import build as build_orig
import distutils.sysconfig


LIBJPEG_SRC = os.path.join('pylibjpeg', 'src', 'libjpeg')
PYLIBJPEG_SRC = os.path.join('pylibjpeg', 'src', 'pylibjpeg')


# Workaround for needing cython and numpy
# Solution from: https://stackoverflow.com/a/54128391/12606901
class build(build_orig):
    def finalize_options(self):
        super().finalize_options()
        __builtins__.__NUMPY_SETUP__ = False

        import numpy
        for ext in self.distribution.ext_modules:
            if ext in extensions:
                ext.include_dirs.append(numpy.get_include())


def get_mscv_args():
    """Return a list of compiler args for MSVC++'s compiler."""
    flags = [
        '/GS',  # Buffer security check
        '/W3',  # Warning level
        '/wd"4335"',  # Ignore warning 4335
        '/Zc:wchar_t',  # Use windows char type
        '/Zc:inline',  # Remove unreferenced function or data (...)
        '/Zc:forScope',
        '/Od',  # Disable optimisation
        '/Oy-',  # (x86 only) don't omit frame pointer
        '/openmp-',  # Disable #pragma omp directive
        '/FC',  # Display full path of source code files
        '/fp:precise',  # Floating-point behaviour
        '/Gd',  # (x86 only) use __cdecl calling convention
        '/GF-',  # Disable string pooling
        '/GR',  # Enable run-time type info
        '/RTC1',  # Enable run-time error checking
        # /D defines constants and macros
        '/D_UNICODE',
        '/DUNICODE',
    ]
    # Set the architecture based on system architecture and Python
    is_x64 = platform.architecture()[0] == '64bit'
    if is_x64 and sys.maxsize > 2**32:
        flags.append('/DWIN64=1')
    else:
        # Architecture is 32-bit, or Python is 32-bit
        flags.append('/DWIN32=1')

    return flags


def get_gcc_args():
    """Return a list of compiler and linker args for GCC/clang.

    The args are determined by running the src/libjpeg/configure script then
    parsing src/libjpeg/automakefile for the relevant values.

    Returns
    -------
    dict
        A dict with keys COMPILER_CMD, CC_ONLY, SETTINGS, PREFIX,
        PTHREADCFLAGS, PTHREADLDFLAGS, PTHREADLIBS, HWTYPE, HAVE_ADDONS,
        BITSIZE, ADDOPTS, LIB_OPTS, EXTRA_LIBS, CPU, TUNE.
    """
    # Run configure script once
    # Using GCC or clang, run `configure` bash script once
    if 'config.log' not in os.listdir(LIBJPEG_SRC):
        # Needs to be determined before changing the working dir
        fpath = os.path.abspath(LIBJPEG_SRC)
        # Needs to be run from within the src/libjpeg directory
        current_dir = os.getcwd()
        os.chdir(LIBJPEG_SRC)
        subprocess.call([os.path.join(fpath, 'configure')])
        os.chdir(current_dir)

    # Get compilation options
    with open(os.path.join(LIBJPEG_SRC, 'automakefile')) as fp:
        lines = fp.readlines()

    lines = [ll for ll in lines if not ll.startswith('#')]
    opts = [ll.split('=', 1) for ll in lines]
    opts = {vv[0].strip():list(vv[1].strip().split(' ')) for vv in opts}

    return opts


def get_source_files():
    """Return a list of paths to the source files to be compiled."""
    source_files = [
        'pylibjpeg/_libjpeg.pyx',
        os.path.join(PYLIBJPEG_SRC, 'decode.cpp'),
        os.path.join(PYLIBJPEG_SRC, 'streamhook.cpp'),
    ]
    for fname in Path(LIBJPEG_SRC).glob('*/*'):
        if '.cpp' in str(fname):
            source_files.append(str(fname))

    return source_files


# Compiler and linker arguments
extra_compile_args = []
extra_link_args = []
if platform.system() == 'Windows':
    os.environ['LIB'] == os.path.join(sys.executable, '../', 'libs')
    extra_compile_args = get_mscv_args()
elif platform.system() in ['Darwin', 'Linux']:
    opts = get_gcc_args()
    extra_compile_args += opts['ADDOPTS']
    extra_link_args += opts['EXTRA_LIBS']


extensions = [
    Extension(
        '_libjpeg',
        get_source_files(),
        language='c++',
        include_dirs=[
            LIBJPEG_SRC,
            PYLIBJPEG_SRC,
            distutils.sysconfig.get_python_inc(),
            # Numpy includes get added by the `build` subclass
        ],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

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
        "jpg jpeg jpg-ls jpeg-ls libjpeg pylibjpeg"
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
        "Operating System :: Microsoft :: Windows",  # Tested OK
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
    cmdclass = {'build': build},
    ext_modules = extensions,
)
