"""Parsers for 10918 JPEG segments.

For parameters which are 2 bytes, the most significant byte shall come first
in the compressed data's ordered sequence of bytes. Parameters which are 4
bits in length always come in pairs and the pair shall always be encoded as
a single byte. The first 4-bit parameter of the pair shall occupy the most
significant 4 bits of the byte. Within and 16-, 8- or 4-bit parameter the
MSB shall come first and the LSB shall come last.

BIG ENDIAN.

Non-hierarchical

SOI | Frame | EOI

Frame
[Tables/misc] | SOF Frame header | Scan_1 | [DNL segment] | [Scan_2] ... | [Scan_n] |

Scan
[Tables/misc] | Scan header | [ECS_0 | RST_0 | ... | RST_n] | ECS_n |

ECS
<MCU1>, <MCU_2>, ..., <MCU_R>

----------------------------------------------------------

**Marker Segments**

A marker segments consists of a marker followed by a sequence of related
parameters. The first parameter is the two-byte length parameter, which encodes
the number of bytes in the marker segment (including the length parameter and
excluding the two-byte marker).

The SOF and SOS marker segments are referred to as the frame header and the
scan header, respectively.

See ISO/IEC 10918-1, Section B.1.1.4

The following marker segments are supported:

* APP
* COM
* DAC
* DHT
* DNL
* DQT
* DRI
* EXP
* SOF
* SOS
"""

from struct import unpack
from typing import BinaryIO, Any, cast, Dict, Union, List, Tuple

from pylibjpeg.tools.utils import split_byte


def APP(fp: BinaryIO) -> Dict[str, Union[int, bytes]]:
    """Return a dict containing APP data.

    See ISO/IEC 10918-1 Section B.2.4.6.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``Lp`` : application data segment length
        * ``Ap`` : application data
    """
    length = unpack(">H", fp.read(2))[0]

    return {"Lp": length, "Ap": fp.read(length - 2)}


def COM(fp: BinaryIO) -> Dict[str, Union[int, str]]:
    """Return a dict containing COM data.

    See ISO/IEC 10918-1 Section B.2.4.5.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``Lc`` : comment data segment length
        * ``Cm`` : comment bytes
    """
    length = unpack(">H", fp.read(2))[0]
    comment = unpack("{}s".format(length - 2), fp.read(length - 2))[0]

    return {"Lc": length, "Cm": comment}


def DAC(fp: BinaryIO) -> Dict[str, Union[int, List[int]]]:
    """Return a dict containing DAC segment data.

    See ISO/IEC 10918-1 Section B.2.4.3.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``La`` : arithmetic coding conditioning definition length
        * ``Tc`` : table class (0 for DC or lossless, 1 for AC)
        * ``Tb`` : arithmetic coding conditioning table destination identifier
        * ``Cs`` : conditioning table value
    """
    length = unpack(">H", fp.read(2))[0]
    bytes_to_read = length - 2

    tc, tb, cs = [], [], []
    while bytes_to_read > 0:
        _tc, _tb = split_byte(fp.read(1))
        cs.append(unpack(">B", fp.read(1))[0])
        tc.append(_tc)
        tb.append(_tb)

        bytes_to_read -= 2

    return {"La": length, "Tc": tc, "Tb": tb, "Cs": cs}


def DHT(fp: BinaryIO) -> Dict[str, Union[int, List[int], Any]]:
    """Return a dict containing DHT segment data.

    See ISO/IEC 10918-1 Section B.2.4.2.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``Lh`` : Huffman table definition length
        * ``Tc`` : table class (0 for DC or lossless, 1 for AC)
        * ``Th`` : Huffman table destination identifier, one of four possible
          destinations at the decoder into which the table shall be installed
        * ``Li`` : number of Huffman codes of length *i*, equivalent to the
          list *BITS*
        * ``Vij`` : value associated with each Huffman code of length *i*,
          equivalent to *HUFFVAL*
    """
    length = unpack(">H", fp.read(2))[0]
    bytes_to_read = length - 2

    tc, th, li = [], [], []
    vij: Dict[Tuple[int, int], Dict[int, Tuple[int]]] = {}
    while bytes_to_read > 0:
        _tc, _th = split_byte(fp.read(1))
        tc.append(_tc)
        th.append(_th)

        bytes_to_read -= 1

        # li (BITS) is the number of codes for each code length, from 1 to 16
        _li = unpack(">16B", fp.read(16))
        bytes_to_read -= 16

        # vij is a list of the 8-bit symbols values (HUFFVAL), each of which
        #   is assigned a Huffman code.
        _vij = {}
        for ii in range(16):
            nr = _li[ii]
            if nr:
                _vij[ii + 1] = unpack(f">{nr}B", fp.read(nr))
                bytes_to_read -= nr

        li.append(_li)
        vij[(_tc, _th)] = _vij

    return {"Lh": length, "Tc": tc, "Th": th, "Li": li, "Vij": vij}


def DNL(fp: BinaryIO) -> Dict[str, Union[int, List[int]]]:
    """Return a dict containing DNL segment data.

    See ISO/IEC 10918-1 Section B.2.5.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``Ld`` : DNL segment length
        * ``NL`` : number of lines in the frame
    """
    length = unpack(">H", fp.read(2))[0]
    nr_lines = unpack(">H", fp.read(2))[0]

    return {"Ld": length, "NL": nr_lines}


def DQT(fp: BinaryIO) -> Dict[str, Union[int, List[int], List[List[int]]]]:
    """Return a dict containing DQT segment data.

    See ISO/IEC 10918-1 Section B.2.4.1.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``Lq`` : quantization table definition length
        * ``Pq`` : quantization table element precision
        * ``Tq`` : quantization table destination identifier
        * ``Qk`` : quantization table element
    """
    # length is 2 + sum(t=1, N) of (65 + 64 * Pq(t))
    length = unpack(">H", fp.read(2))[0]
    bytes_to_read = length - 2

    pq, tq, qk = [], [], []
    while bytes_to_read > 0:
        precision, table_id = split_byte(fp.read(1))
        bytes_to_read -= 1
        pq.append(precision)
        tq.append(table_id)

        if precision not in (0, 1):
            raise ValueError(f"JPEG 10918 - DQT: invalid precision '{precision}'")

        # If Pq is 0, Qk is 8-bit, if Pq is 1, Qk is 16-bit
        Q_k = []
        for ii in range(64):
            if precision == 0:
                Q_k.append(cast(int, unpack(">B", fp.read(1))[0]))
                bytes_to_read -= 1
            elif precision == 1:
                Q_k.append(cast(int, unpack(">H", fp.read(2))[0]))
                bytes_to_read -= 2

        qk.append(Q_k)

    return {"Lq": length, "Pq": pq, "Tq": tq, "Qk": qk}


def DRI(fp: BinaryIO) -> Dict[str, int]:
    """Return a dict containing DRI segment data.

    See ISO/IEC 10918-1 Section B.2.4.4.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``Lr`` : DRI segment length
        * ``Ri`` : restart interval (number of MCU in the restart interval)
    """
    return {"Lr": unpack(">H", fp.read(2))[0], "Ri": unpack(">H", fp.read(2))[0]}


def EXP(fp: BinaryIO) -> Dict[str, int]:
    """Return a dict containing EXP segment data.

    See ISO/IEC 10918-1 Section B.3.3.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``Le`` : EXP segment length
        * ``Eh`` : expand horizontally
        * ``Ev`` : expand vertically
    """
    length = unpack(">H", fp.read(2))[0]
    eh, ev = split_byte(unpack(">B", fp.read(1))[0])

    return {"Le": length, "Eh": eh, "Ev": ev}


def SOF(fp: BinaryIO) -> Dict[str, Union[int, Dict[int, Dict[str, int]]]]:
    """Return a dict containing SOF header data.

    See ISO/IEC 10918-1 Section B.2.2.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``Lf`` : frame header length
        * ``P`` : sample precision
        * ``Y`` : number of lines
        * ``X`` : number of samples per line
        * ``Nf`` : number of image components in frame
        * ``Ci`` : component identifier
        * ``Hi`` : horizontal sampling factor
        * ``Vi`` : vertical sampling factor
        * ``Tqi`` : quantization table destination selector
    """
    (length, precision, nr_lines, samples_per_line, nr_components) = unpack(
        ">HBHHB", fp.read(8)
    )

    component_id = {}
    # horizontal_sampling_factor = []
    # vertical_sampling_factor = []
    # quantisation_selector = []
    for ii in range(nr_components):
        _ci = unpack(">B", fp.read(1))[0]
        _hor, _vert = split_byte(fp.read(1))
        # horizontal_sampling_factor.append(_hor)
        # vertical_sampling_factor.append(_vert)
        _tqi = unpack(">B", fp.read(1))[0]
        # quantisation_selector.append(_tqi)

        component_id[_ci] = {
            "Hi": _hor,
            "Vi": _vert,
            "Tqi": _tqi,
        }

    return {
        "Lf": length,
        "P": precision,
        "Y": nr_lines,
        "X": samples_per_line,
        "Nf": nr_components,
        "Ci": component_id,
    }


def SOS(fp: BinaryIO) -> Dict[str, Union[int, List[int]]]:
    """Return a dict containing SOS header data.

    See ISO/IEC 10918-1 Section B.2.3.

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.

    Returns
    -------
    dict
        A dict with keys:

        * ``Ls`` : scan header length
        * ``Ns`` : number of image components in scan
        * ``Csj`` : scan component selector
        * ``Tdj`` : DC entropy coding table destination selector.
        * ``Taj`` : AC entropy coding table destination selector. Set to 0 for
          lossless.
        * ``Ss`` : start of spectral or predictor selection. Shall be 0 for
          sequential DCT, for lossless this is the predictor.
        * ``Se`` : end of spectral selection. Shall be 63 for sequential DCT.
          In lossless this has no meaning and shall be set to 0.
        * ``Ah`` : successive approximation bit position high. In lossless
          this has no meaning and shall be set to 0.
        * ``Al`` : successive approximation bit position low or point transform
          Shall be set to 0 for sequential DCT. In lossless mode specifies
          the point transform Pt.
    """
    (length, nr_components) = unpack(">HB", fp.read(3))

    csj, tdj, taj = [], [], []
    for ii in range(nr_components):
        _cs = unpack(">B", fp.read(1))[0]
        csj.append(_cs)
        _td, _ta = split_byte(fp.read(1))
        tdj.append(_td)
        taj.append(_ta)

    (ss, se) = unpack(">BB", fp.read(2))
    ah, al = split_byte(fp.read(1))

    return {
        "Ls": length,
        "Ns": nr_components,
        "Csj": csj,
        "Tdj": tdj,
        "Taj": taj,
        "Ss": ss,
        "Se": se,
        "Ah": ah,
        "Al": al,
    }


def skip(fp: BinaryIO) -> None:
    """Skip the next N - 2 bytes.

    See ISO/IEC 10918-1 Section ???

    After returning, `fp` will be positioned at the end of the current marker
    segment.

    Parameters
    ----------
    fp : file-life
        A file-like positioned at the start of the length byte for the current
        marker segment.
    """
    length = unpack(">H", fp.read(2))[0]
    fp.seek(length - 2, 1)
