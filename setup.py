import os
from setuptools import setup, find_packages
import sys


VERSION_FILE = os.path.join('pylibjpeg', '_version.py')
with open(VERSION_FILE) as fp:
    exec(fp.read())

with open('README.md', 'r') as fp:
    long_description = fp.read()

setup(
    name = 'pylibjpeg',
    description = (
        "A Python framework for decoding JPEG files, with a focus on "
        "supporting pydicom"
    ),
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    version = __version__,
    author = "scaramallion",
    author_email = "scaramallion@users.noreply.github.com",
    url = "https://github.com/pydicom/pylibjpeg",
    license = "MIT",
    keywords = (
        "dcm dicom pydicom python medicalimaging radiology radiotherapy "
        "oncology imaging jpg jpeg jpg-ls jpeg-ls libjpeg pylibjpeg "
    ),
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        #"Development Status :: 3 - Alpha",
        #"Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries",
    ],
    packages = find_packages(),
    install_requires = ['numpy', 'pylibjpeg-openjpeg'],
    include_package_data = True,
    zip_safe = False,
    python_requires = ">=3.6",
)
