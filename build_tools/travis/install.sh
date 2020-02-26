#!/bin/bash

set -e

#pip install coverage
pip install pytest-cov
pip install pytest
#pip install asv


echo ""
echo "Test suite: " $TEST_SUITE
echo "Working directory: " $PWD
echo ""

if [[ "$TEST_SUITE" == "pydicom_master" ]]; then
    pip install git+https://github.com/pydicom/pydicom.git
    python -c "import pydicom; print('pydicom version', pydicom.__version__)"
elif [[ "$TEST_SUITE" == "pydicom_release" ]]; then
    pip install pydicom
    python -c "import pydicom; print('pydicom version', pydicom.__version__)"
elif [[ "$TEST_SUITE" == 'osx' ]]; then
    pip install pydicom
    python -c "import pydicom; print('pydicom version', pydicom.__version__)"
fi

python --version
