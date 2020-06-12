"""Utilities for pydicom and DICOM pixel data"""

from pkg_resources import iter_entry_points


def generate_frames(ds):
    """Yield decompressed pixel data frames as :class:`numpy.ndarray`.

    Parameters
    ----------
    ds : pydicom.dataset.Dataset
        The dataset containing the pixel data.

    Yields
    ------
    numpy.ndarray
        A single frame of the decompressed pixel data.
    """
    from pydicom.encaps import generate_pixel_data_frame
    from pydicom.pixel_data_handlers.util import pixel_dtype

    decoders = get_pixel_data_decoders()
    decode = decoders[ds.file_meta.TransferSyntaxUID]

    p_interp = ds.PhotometricInterpretation
    nr_frames = getattr(ds, 'NumberOfFrames', 1)
    for frame in generate_pixel_data_frame(ds.PixelData, nr_frames):
        arr = decode(frame, ds.group_dataset(0x0028)).view(pixel_dtype(ds))
        yield reshape_frame(ds, arr)


def get_pixel_data_decoders():
    """Return a :class:`dict` of {UID: callable}."""
    return {
        val.name: val.load()
        for val in iter_entry_points('pylibjpeg.pixel_data_decoders')
    }


def reshape_frame(ds, arr):
    """Return a reshaped :class:`numpy.ndarray` `arr`.

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
