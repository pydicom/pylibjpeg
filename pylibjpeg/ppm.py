"""Utilities for PPM handling."""


def ppmread(fpath):
    pass


class PPM(object):
    def __init__(self, data):
        """
        P1 B&W, ascii
        P2 monochrome, 8- or 16-bit, ascii
        P3 RGB, 3x8-bit, ascii
        P4 B&W, binary
        P5 monochrome, 8- or 16-bit, binary
        P6 RGB, 3x8-bit, binary
        P7 PAM file
        """
        pass

    def save(self, fpath, as_binary=True, endianness='>'):
        pass

    def to_array(self):
        pass

    @property
    def width(self):
        pass

    @property
    def height(self):
        pass

    @property
    def depth(self):
        pass

    @property
    def components(self):
        pass
