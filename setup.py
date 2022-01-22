import os
from pathlib import Path
from setuptools import setup, find_packages
import sys


PACKAGE_DIR = Path(__file__).parent / "pylibjpeg"


with open(PACKAGE_DIR / "_version.py") as f:
    exec(f.read())

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pylibjpeg",
    description=(
        "A Python framework for decoding JPEG and decoding/encoding DICOM "
        "RLE data, with a focus on supporting pydicom"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=__version__,
    author="scaramallion",
    author_email="scaramallion@users.noreply.github.com",
    url="https://github.com/pydicom/pylibjpeg",
    license="MIT",
    keywords=(
        "dcm dicom pydicom python imaging jpg jpeg jpg-ls jpeg-ls jpeg2k "
        "jpeg2000 rle libjpeg pylibjpeg "
    ),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries",
    ],
    packages=find_packages(),
    extras_require={
        "rle": ["pylibjpeg-rle"],
        "openjpeg": ["pylibjpeg-openjpeg"],
        "libjpeg": ["pylibjpeg-libjpeg"],
        "all": ["pylibjpeg-libjpeg", "pylibjpeg-openjpeg", "pylibjpeg-rle"],
    },
    install_requires=["numpy"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
)
