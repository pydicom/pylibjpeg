
import os

from pylibjpeg.data.ds import (
    JPEG2000_IDX, JPEG2000Lossless_IDX, JPEGBaseline_IDX,
    JPEGExtended_IDX, JPEGLossless_IDX, JPEGLosslessSV1_IDX,
    JPEGLS_IDX, JPEGLSLossless_IDX,  LittleEndianExplicit_IDX
)

DATA_DIR = os.path.abspath(os.path.dirname(__file__))
DS_DIR = os.path.join(DATA_DIR, 'ds')
JPG10918_DIR = os.path.join(DATA_DIR, 'jpg10918')  # JPEG
JPG14495_DIR = os.path.join(DATA_DIR, 'jpg14495')  # JPEG-LS
JPG15444_DIR = os.path.join(DATA_DIR, 'jpg15444')  # JPEG2000


def _add_element(elem):
    return (
        "            {} : ({}, {}),\n".format(elem.tag, elem.VR, elem.value)
    )


def add_dataset(ds, fname, source):
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


def get_dataset(fname):
    pass

def get_datasets(uid=None, as_dataset=False):
    """
    """
    uids = {
        '1.2.840.10008.1.2.1' : 'LittleEndianExplicit',
        '1.2.840.10008.1.2.4.50' : 'JPEGBaseline',
        '1.2.840.10008.1.2.4.51' : 'JPEGExtended',
        '1.2.840.10008.1.2.4.57' : 'JPEGLossless',
        '1.2.840.10008.1.2.4.70' : 'JPEGLosslessSV1',
        '1.2.840.10008.1.2.4.80' : 'JPEGLSLossless',
        '1.2.840.10008.1.2.4.81' : 'JPEGLS',
        '1.2.840.10008.1.2.4.90' : 'JPEG2000Lossless',
        '1.2.840.10008.1.2.4.91' : 'JPEG2000',
    }
    subdir = uids[uid]
    fnames = get_indices('ds')[subdir].keys()
    fpaths = os.path.join(DS_DIR, subdir, fname)
    if as_dataset:
        return [dcmread(fpath) for fpath in fpaths]

    return fpaths


def get_indices(index_type='ds'):
    """Return a :class:`dict` containing all the indices for `index_type`.

    Parameters
    ----------
    index_type : str
        The index type to get, one of ``'ds'``.
    """
    if index_type == 'ds':
        return {
            'LittleEndianExplicit' : LittleEndianExplicit_IDX,
            'JPEGBaseline' : JPEGBaseline_IDX,
            'JPEGExtended' : JPEGExtended_IDX,
            'JPEGLossless' : JPEGLossless_IDX,
            'JPEGLosslessSV1' : JPEGLosslessSV1_IDX,
            'JPEGLSLossless' : JPEGLSLossless_IDX,
            'JPEGLS' : JPEGLS_IDX,
            'JPEG2000Lossless' : JPEG2000Lossless_IDX,
            'JPEG2000' : JPEG2000_IDX,
        }
