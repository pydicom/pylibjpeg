import logging
import os
from typing import BinaryIO, Union, cast

from .s10918 import parse, JPEG


LOGGER = logging.getLogger(__name__)
PARSERS = {"10918": (parse, JPEG)}


def get_specification(fp: BinaryIO) -> str:
    """ """
    if fp.read(1) != b"\xff":
        raise ValueError("File is not JPEG")

    # Skip any initial fill bytes
    while fp.read(1) == b"\xff":
        pass

    fp.seek(-2, 1)

    # Confirm SOI marker
    marker = fp.read(2)

    if marker == b"\xFF\xD8":
        fp.seek(0)
        return "10918"

    s = "".join(f"{x:02X}" for x in marker)
    raise NotImplementedError(
        f"Reading a JPEG file with first marker '{s}' is not supported"
    )


def jpgread(path: Union[str, os.PathLike[str], BinaryIO]) -> JPEG:
    """Return a represention of the JPEG file at `fpath`."""
    LOGGER.debug(f"Reading file: {path}")
    if not hasattr(path, "read"):
        path = cast(str, path)
        with open(path, "rb") as fp:
            jpg_format = get_specification(fp)
            parser, jpg_class = PARSERS[jpg_format]
            meta = parser(fp)
            LOGGER.debug("File parsed successfully")
    else:
        path = cast(BinaryIO, path)
        jpg_format = get_specification(path)
        parser, jpg_class = PARSERS[jpg_format]
        meta = parser(path)
        LOGGER.debug("File parsed successfully")

    return jpg_class(meta)
