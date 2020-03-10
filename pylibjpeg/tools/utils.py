"""Utility functions."""


def get_bit(byte, index):
    """Return the value of the bit at `index` of `byte`.

    Parameters
    ----------
    byte : bytes
        The value to process.
    index : int
        The index of the bit to return, where index ``0`` is the most
        significant bit and index ``7`` is the least significant.

    Returns
    -------
    int
        The value of the bit (0 or 1).
    """
    byte = ord(byte[:1])
    if not (-1 < index < 8):
        raise ValueError("'index' must be between 0 and 7, inclusive")

    return (byte >> (7 - index)) & 1


def split_byte(byte):
    """Return the 8-bit `byte` as two 4-bit unsigned integers.

    Parameters
    ----------
    byte : bytes
        The byte to split, if more than one byte is supplied only the first
        will be split.

    Returns
    -------
    2-tuple of int
        The (4 most significant, 4 least significant) bits of `byte` as ``(int,
        int)``.
    """
    byte = ord(byte[:1])
    return byte >> 4, 0b00001111 & byte
