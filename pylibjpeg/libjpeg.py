
import _libjpeg


def decode(arr, nr_bytes):
    """Return the decoded JPEG data from `arr`.

    Parameters
    ----------
    arr : numpy.ndarray
        A 1D array of np.uint8 containing the raw encoded JPEG image.
    nr_bytes : int
        The expected length of the uncompressed image data in bytes.

    Returns
    -------
    numpy.ndarray
        A 1D array of np.uint8 containing the decoded image data.
    """
    return _libjpeg.decode(arr, nr_bytes)
