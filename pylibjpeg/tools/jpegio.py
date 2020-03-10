
import logging

from .s10918 import parse, JPEG


LOGGER = logging.getLogger('pylibjpeg.tools.jpegio')
PARSERS = {
    '10918' : (parse, JPEG),
}


def get_specification(fp):
    """
    """
    if fp.read(1) != b'\xff':
        raise ValueError('File is not JPEG')

    # Skip any initial fill bytes
    while fp.read(1) == b'\xff':
        pass

    fp.seek(-2, 1)

    # Confirm SOI marker
    marker = fp.read(2)

    if marker == b'\xFF\xD8':
        fp.seek(0)
        return '10918'

    raise NotImplementedError(
        "Reading a JPEG file with first marker '0x{}' is not supported"
        .format(marker)
    )


def jpgread(fpath):
    """Return a represention of the JPEG file at `fpath`."""
    LOGGER.debug("Reading file: {}".format(fpath))
    if isinstance(fpath, str):
        with open(fpath, 'rb') as fp:
            jpg_format = get_specification(fp)
            parser, jpg_class = PARSERS[jpg_format]
            meta = parser(fp)
            LOGGER.debug("File parsed successfully")
    else:
        jpg_format = get_specification(fpath)
        parser, jpg_class = PARSERS[jpg_format]
        meta = parser(fpath)
        LOGGER.debug("File parsed successfully")

    return jpg_class(meta)
