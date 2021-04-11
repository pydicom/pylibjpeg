"""Utilities for pydicom and DICOM pixel data

.. deprecated:: 1.2

    Use pydicom's pylibjpeg pixel data handler instead.
"""

from pylibjpeg.utils import get_pixel_data_decoders


def generate_frames(ds):
    """Yield decompressed pixel data frames as :class:`numpy.ndarray`.

    .. deprecated:: 1.2

        Use
        :func:`~pydicom.pixel_data_handlers.pylibjpeg_handler.generate_frames`
        instead

    Parameters
    ----------
    ds : pydicom.dataset.Dataset
        The dataset containing the pixel data.

    Yields
    ------
    numpy.ndarray
        A single frame of the decompressed pixel data.
    """
    try:
        import pydicom
    except ImportError:
        raise RuntimeError(
            "'generate_frames' requires the pydicom package"
        )

    from pydicom.encaps import generate_pixel_data_frame
    from pydicom.pixel_data_handlers.util import pixel_dtype

    decoders = get_pixel_data_decoders()
    decode = decoders[ds.file_meta.TransferSyntaxUID]

    p_interp = ds.PhotometricInterpretation
    nr_frames = getattr(ds, 'NumberOfFrames', 1)
    for frame in generate_pixel_data_frame(ds.PixelData, nr_frames):
        arr = decode(frame, ds.group_dataset(0x0028)).view(pixel_dtype(ds))
        yield reshape_frame(ds, arr)


def reshape_frame(ds, arr):
    """Return a reshaped :class:`numpy.ndarray` `arr`.

    .. deprecated:: 1.2

        Use pydicom instead.

    +------------------------------------------+-----------+----------+
    | Element                                  | Supported |          |
    +-------------+---------------------+------+ values    |          |
    | Tag         | Keyword             | Type |           |          |
    +=============+=====================+======+===========+==========+
    | (0028,0002) | SamplesPerPixel     | 1    | N > 0     | Required |
    +-------------+---------------------+------+-----------+----------+
    | (0028,0006) | PlanarConfiguration | 1C   | 0, 1      | Optional |
    +-------------+---------------------+------+-----------+----------+
    | (0028,0010) | Rows                | 1    | N > 0     | Required |
    +-------------+---------------------+------+-----------+----------+
    | (0028,0011) | Columns             | 1    | N > 0     | Required |
    +-------------+---------------------+------+-----------+----------+

    (0028,0006) *Planar Configuration* is required when (0028,0002) *Samples
    per Pixel* is greater than 1. For certain compressed transfer syntaxes it
    is always taken to be either 0 or 1 as shown in the table below.

    +---------------------------------------------+-----------------------+
    | Transfer Syntax                             | Planar Configuration  |
    +------------------------+--------------------+                       |
    | UID                    | Name               |                       |
    +========================+====================+=======================+
    | 1.2.840.10008.1.2.4.50 | JPEG Baseline      | 0                     |
    +------------------------+--------------------+-----------------------+
    | 1.2.840.10008.1.2.4.57 | JPEG Lossless,     | 0                     |
    |                        | Non-hierarchical   |                       |
    +------------------------+--------------------+-----------------------+
    | 1.2.840.10008.1.2.4.70 | JPEG Lossless,     | 0                     |
    |                        | Non-hierarchical,  |                       |
    |                        | SV1                |                       |
    +------------------------+--------------------+-----------------------+
    | 1.2.840.10008.1.2.4.80 | JPEG-LS Lossless   | 1                     |
    +------------------------+--------------------+-----------------------+
    | 1.2.840.10008.1.2.4.81 | JPEG-LS Lossy      | 1                     |
    +------------------------+--------------------+-----------------------+
    | 1.2.840.10008.1.2.4.90 | JPEG 2000 Lossless | 0                     |
    +------------------------+--------------------+-----------------------+
    | 1.2.840.10008.1.2.4.91 | JPEG 2000 Lossy    | 0                     |
    +------------------------+--------------------+-----------------------+

    Parameters
    ----------
    ds : dataset.Dataset
        The :class:`~pydicom.dataset.Dataset` containing the Image Pixel module
        corresponding to the data in `arr`.
    arr : numpy.ndarray
        The 1D array containing the pixel data.

    Returns
    -------
    numpy.ndarray
        A reshaped array containing the pixel data. The shape of the array
        depends on the contents of the dataset:

        * For single frame, single sample data (rows, columns)
        * For single frame, multi-sample data (rows, columns, planes)

    References
    ----------

    * DICOM Standard, Part 3,
      :dcm:`Annex C.7.6.3.1<part03/sect_C.7.6.3.html#sect_C.7.6.3.1>`
    * DICOM Standard, Part 5, :dcm:`Section 8.2<part05/sect_8.2.html>`
    """
    # Transfer Syntax UIDs that are always Planar Configuration 0
    conf_zero = [
        '1.2.840.10008.1.2.4.50',
        '1.2.840.10008.1.2.4.57',
        '1.2.840.10008.1.2.4.70',
        '1.2.840.10008.1.2.4.90',
        '1.2.840.10008.1.2.4.91'
    ]
    # Transfer Syntax UIDs that are always Planar Configuration 1
    conf_one = [
        '1.2.840.10008.1.2.4.80',
        '1.2.840.10008.1.2.4.81',
    ]

    # Valid values for Planar Configuration are dependent on transfer syntax
    nr_samples = ds.SamplesPerPixel
    if nr_samples > 1:
        transfer_syntax = ds.file_meta.TransferSyntaxUID
        if transfer_syntax in conf_zero:
            planar_configuration = 0
        elif transfer_syntax in conf_one:
            planar_configuration = 1
        else:
            planar_configuration = ds.PlanarConfiguration

        if planar_configuration not in [0, 1]:
            raise ValueError(
                "Unable to reshape the pixel array as a value of {} for "
                "(0028,0006) 'Planar Configuration' is invalid."
                .format(planar_configuration)
            )

    if nr_samples == 1:
        # Single plane
        arr = arr.reshape(ds.Rows, ds.Columns)  # view
    else:
        # Multiple planes, usually 3
        if planar_configuration == 0:
            arr = arr.reshape(ds.Rows, ds.Columns, nr_samples)  # view
        else:
            arr = arr.reshape(nr_samples, ds.Rows, ds.Columns)
            arr = arr.transpose(1, 2, 0)

    return arr


def get_j2k_parameters(codestream):
    """Return some of the JPEG 2000 component sample's parameters in `stream`.

    .. deprecated:: 1.2

        Use :func:`~pydicom.pixel_data_handlers.utils.get_j2k_parameters`
        instead

    Parameters
    ----------
    codestream : bytes
        The JPEG 2000 (ISO/IEC 15444-1) codestream data to be parsed.

    Returns
    -------
    dict
        A dict containing the JPEG 2000 parameters for the first component
        sample, will be empty if `codestream` doesn't contain JPEG 2000 data or
        if unable to parse the data.
    """
    try:
        # First 2 bytes must be the SOC marker - if not then wrong format
        if codestream[0:2] != b'\xff\x4f':
            return {}

        # SIZ is required to be the second marker - Figure A-3 in 15444-1
        if codestream[2:4] != b'\xff\x51':
            return {}

        # See 15444-1 A.5.1 for format of the SIZ box and contents
        ssiz = ord(codestream[42:43])
        parameters = {}
        if ssiz & 0x80:
            parameters['precision'] = (ssiz & 0x7F) + 1
            parameters['is_signed'] = True
        else:
            parameters['precision'] = ssiz + 1
            parameters['is_signed'] = False

        return parameters

    except (IndexError, TypeError):
        return {}
