
import os


DATA_DIR = os.path.abspath(os.path.dirname(__file__))
DS_INDEX = ps.path.join(DATA_DIR, 'ds', 'index.py')
JPG10918_INDEX = ps.path.join(DATA_DIR, 'jpg10918', 'index.py')  # JPEG
JPG14495_INDEX = ps.path.join(DATA_DIR, 'jpg14495', 'index.py')  # JPEG-LS
JPG15444_INDEX = ps.path.join(DATA_DIR, 'jpg15444', 'index.py')  # JPEG2000


def _add_element(elem):
    return (
        "            {} : ({}, {}),\n".format(elem.tag, elem.VR, elem.value)
    )


def add_dataset(ds, fname, source, ):
    """Add a dataset to the managed data.

    Parameters
    ----------
    fpath
    """
    import pylibjpeg.data.ds.index.DATA as DATA

    # Check if file already exists in index
    if os.path.basename(fname) in DATA:
        raise ValueError(
            "A dataset with the filename '{}' already exists".format(fpath)
        )

    ds.save_as(os.path.join(DATA_DIR, 'ds', fname), write_like_original=False)
    with open(DS_INDEX, 'r') as index:
        lines = index.readlines()

    """
        'filename' : {
            0x00020010 : (VR, value),  # Transfer Syntax UID
            0x00280010 : (VR, value),  # (0028,xxxx) elements
            ...
        }
    """
    entry =   ["        '{}': {\n".format(fname)]
    entry.append(_add_element(ds.file_meta['TransferSyntaxUID']))
    if 'NumberOfFrames' not in ds:
        ds.NumberOfFrames = 1
    if 'PlanarConfiguration' not in ds:
        ds.PlanarConfiguration = 0

    for elem in ds[0x00280000:0x00290000]:
        keyword = elem.keyword
        entry.append(ds[keyword])

    lines = lines[:-1] + entry + lines[-1]

    with open(DS_INDEX, 'w') as index:
        for line in lines:
            index.write(line)


def add_jpg(fname):
    pass


def get_jpg(fname):
    pass


def get_dataset(fname):
    pass
