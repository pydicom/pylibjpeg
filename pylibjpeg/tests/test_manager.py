
import os
from tempfile import NamedTemporaryFile

import pytest

from pylibjpeg.data.manager import DATA_DIR


def TestManager_AddDataset(object):
    """Tests for manager.add_dataset."""
    def setup(self):
        """Setup env for tests."""
        self.tfile = NamedTemporaryFile()
        self.original = pylibjpeg.data.manager.DS_INDEX
        pylibjpeg.data.manager.DS_INDEX = self.tfile.name
        with open(self.tfile.name, 'w') as tfile:
            tfile.write("DATASETS = {\n}\n")

    def teardown(self):
        """Reset any changes."""
        pylibjpeg.data.manager.DS_INDEX = self.original

    def test_add_empty(self):
        """Test adding a dataset when the index is empty."""
        fpath = os.path.join(DATA_DIR, 'ds', 'CT_small.dcm')
        ds = dcmread(fpath)
        add_dataset(ds, 'test_name.dcm')
