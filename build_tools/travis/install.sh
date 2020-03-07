#!/bin/bash

set -e

echo ""
echo "Test suite: " $TEST_SUITE
echo "Working directory: " $PWD
echo ""

if [[ "$TEST_SUITE" == "pydicom_master" ]]; then
    pip install pytest pytest-cov
    pip install git+https://github.com/pydicom/pydicom.git
    python -c "import pydicom; print('pydicom version', pydicom.__version__)"
elif [[ "$TEST_SUITE" == "pydicom_release" ]]; then
    pip install pydicom pytest pytest-cov
    python -c "import pydicom; print('pydicom version', pydicom.__version__)"
elif [[ "$TEST_SUITE" == 'osx' ]]; then
    brew update
    brew install openssl readline
    pyenv install $TRAVIS_PYTHON_VERSION
    brew outdated pyenv || brew upgrade pyenv
    brew install pyenv-virtualenv
    export PYENV_VERSION=$TRAVIS_PYTHON_VERSION
    export PATH="$HOME/.pyenv/bin:${PATH}"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    export PATH="/Users/travis/.pyenv/shims:${PATH}"
    pyenv virtualenv venv
    pyenv activate venv
    python --version
    pip install --upgrade pip
    pip install pydicom pytest pytest-cov
    python -c "import pydicom; print('pydicom version', pydicom.__version__)"
elif [[ "$TEST_SUITE" == 'conda' ]]; then
    deactivate

    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
    bash miniconda.sh -b -p $HOME/miniconda
    source "$HOME/miniconda/etc/profile.d/conda.sh"
    hash -r
    conda config --set always_yes yes --set changeps1 no
    conda update -q conda
    # Useful for debugging any issues with conda
    conda info -a
    # Replace dep1 dep2 ... with your dependencies
    conda create -q -n test-environment python=$TRAVIS_PYTHON_VERSION pip
    conda activate test-environment
    conda install --yes nose pytest pytest-cov setuptools
    conda install --yes -c conda-forge pydicom
elif [[ "$TEST_SUITE" == 'windows' ]]; then
    choco install python --version $TRAVIS_PYTHON_VERSION
    ls /c
    ls /c/ProgramData/chocolatey/bin/
    ls /c/Python38
    echo $PATH
    echo $CL
    export PATH="/c/Python38:/c/Python38/Scripts:$PATH"
    python -m pip install --upgrade pip
    python -m pip install pydicom pytest pytest-cov
else
    pip install pytest pytest-cov
fi

python --version
