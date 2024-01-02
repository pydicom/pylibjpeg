""""""

import logging
from struct import unpack
from typing import BinaryIO, Any, Callable, cast, Dict, Tuple

from ._markers import MARKERS


LOGGER = logging.getLogger(__name__)


def parse(fp: BinaryIO) -> Dict[Tuple[str, int], Any]:
    """Return a JPEG but don't decode yet."""
    _fill_bytes = 0
    while fp.read(1) == b"\xff":
        _fill_bytes += 1
        pass

    fp.seek(-2, 1)

    # Confirm SOI marker
    if fp.read(2) != b"\xFF\xD8":
        raise ValueError("SOI marker not found")

    info: Dict[Tuple[str, int], Tuple[int, int, Any]] = {
        ("SOI", fp.tell() - 2): (unpack(">H", b"\xFF\xD8")[0], _fill_bytes, {})
    }

    END_OF_FILE = False

    while True:
        _fill_bytes = 0

        # Skip fill
        next_byte = fp.read(1)
        while next_byte == b"\xFF":
            _fill_bytes += 1
            next_byte = fp.read(1)

        # Remove the byte thats actually part of the marker
        if _fill_bytes:
            _fill_bytes -= 1

        fp.seek(-2, 1)

        _marker = unpack(">H", fp.read(2))[0]

        if _marker in MARKERS:
            name, description, handler = MARKERS[_marker]
            key = (name, fp.tell() - 2)
            if name not in ["SOS", "EOI"]:
                if handler is None:
                    length = unpack(">H", fp.read(2))[0] - 2
                    fp.seek(length, 1)
                    continue

                info[key] = (_marker, _fill_bytes, handler(fp))

            elif name == "SOS":
                # SOS's info dict contains an extra 'encoded_data' keys
                # which use RSTN@offset and ENC@offset
                handler = cast(Callable, handler)
                info[key] = (_marker, _fill_bytes, handler(fp))

                encoded_data = bytearray()
                _enc_start = fp.tell()

                while True:
                    _enc_key = ("ENC", _enc_start - 2)
                    prev_byte = fp.read(1)
                    if prev_byte == b"":
                        END_OF_FILE = True
                        break
                    elif prev_byte != b"\xFF":
                        encoded_data.extend(prev_byte)
                        continue

                    # To get here next_byte must be 0xFF
                    # If the next byte is 0x00 then keep reading
                    # If the next byte is 0xFF then keep reading until
                    #   a non-0xFF byte is found
                    # If the marker is a RST marker then keep reading
                    # Otherwise rewind to the start of the fill bytes and break

                    next_byte = fp.read(1)
                    if next_byte == b"\x00":
                        # Skip padding bytes
                        # The previous byte wasn't added so do it now
                        encoded_data.extend(prev_byte)
                        # encoded_data.extend(next_byte)
                        continue

                    # To get here next_byte must be non-padding (non 0x00)
                    #   so we must be at the end of the encoded data
                    info[key][2].update({_enc_key: encoded_data})
                    encoded_data = bytearray()

                    # The number of 0xFF bytes before the marker
                    #   i.e. 0xFF 0xFF 0xFF 0xD9 is 2 fill bytes
                    _sos_fill_bytes = 0
                    # While we still have 0xFF bytes
                    while next_byte == b"\xFF":
                        _sos_fill_bytes += 1
                        next_byte = fp.read(1)

                    # Check to see if marker is RST_m
                    if next_byte in [
                        b"\xD0",
                        b"\xD1",
                        b"\xD2",
                        b"\xD3",
                        b"\xD4",
                        b"\xD5",
                        b"\xD6",
                        b"\xD7",
                    ]:
                        _sos_marker = unpack(">H", b"\xFF" + next_byte)[0]
                        _sos_marker, _, _ = MARKERS[_sos_marker]
                        _sos_key = (_sos_marker, fp.tell() - 2)
                        info[key][2].update({_sos_key: None})

                        _enc_start = fp.tell()
                        continue

                    # End of the current scan, rewind and break
                    # Back up to the start of the 0xFF
                    # Currently position at first byte after marker
                    fp.seek(-2 - _sos_fill_bytes, 1)
                    break

            elif name == "EOI":
                info[key] = (_marker, _fill_bytes, {})
                break

        else:
            if not END_OF_FILE:
                print(
                    "Unknown marker {} at offset {}".format(hex(_marker), fp.tell() - 2)
                )
                raise NotImplementedError
            else:
                break

    return info
