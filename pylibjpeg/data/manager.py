
import os

try:
    from pydicom import dcmread
except ImportError:
    pass

from pylibjpeg.data.ds import (
    JPEG2000_IDX, JPEG2000Lossless_IDX, JPEGBaseline_IDX,
    JPEGExtended_IDX, JPEGLossless_IDX, JPEGLosslessSV1_IDX,
    JPEGLS_IDX, JPEGLSLossless_IDX,  LittleEndianExplicit_IDX
)

DATA_DIR = os.path.abspath(os.path.dirname(__file__))
DS_DIR = os.path.join(DATA_DIR, 'ds')


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
    fpaths = [os.path.join(DS_DIR, subdir, fname) for fname in fnames]
    if as_dataset:
        return [dcmread(fpath) for fpath in fpaths]

    return fpaths


def get_indexed_datasets(uid):
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
    index = get_indices('ds')[subdir]
    fnames = index.keys()
    for fname in fnames:
        fpath = os.path.join(DS_DIR, subdir, fname)
        index[fname]['ds'] = dcmread(fpath)

    return index


def get_from_parameter(index, keyword, value):
    matches = []
    for kk, vv in index.items():
        if keyword in vv and vv[keyword] == value:
            matches.append(index[kk]['ds'])

    return matches


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
