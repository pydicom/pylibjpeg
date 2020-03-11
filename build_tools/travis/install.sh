#!/bin/bash

set -e

echo ""
echo "Test suite: " $TEST_SUITE
echo "Working directory: " $PWD
echo ""

pip install -U pip
pip install pytest pytest-cov

if [[ "$INSTALL_PYDICOM" == "true" ]]; then
    pip install pydicom
    python -c "import pydicom; print('pydicom version', pydicom.__version__)"
fi

# Install the test data
python -m pip install git+git://github.com/pydicom/pylibjpeg-data
python -c "import data; print('data version', data.__version__)"

# Install plugins
if [[ "$INSTALL_LIBJPEG" == 'true' ]]; then
    python -m pip install git+git://github.com/pydicom/pylibjpeg-libjpeg
    python -c "import libjpeg; print('libjpeg version', libjpeg.__version__)"
fi

python --version
