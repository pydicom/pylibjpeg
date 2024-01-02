"""Printing functions for 10918 JPEG marker segments.

The following segments are supported:

* APP : 0xFFE0 to 0xFFEF
* COM : 0xFFFE
* DAC : 0xFFCC
* DHP : 0xFFDE
* DHT : 0xFFC4
* DQT : 0xFFDB
* DNL : 0xFFDC
* DRI : 0xFFDD
* EOI : 0xFFD9
* EXP : 0xFFDF
* SOF : 0xFFC0 to 0xFFC3, 0xFFC5 to 0xFFC7, 0xFFC9 to 0xFFCB, 0xFFCD to 0xFFCF
* SOI : 0xFFD8
* SOS : 0xFFDA
"""

from struct import unpack
from typing import Any, cast, Tuple, Dict, Union


ZIGZAG = [
    0,
    1,
    5,
    6,
    14,
    15,
    27,
    28,
    2,
    4,
    7,
    13,
    16,
    26,
    29,
    42,
    3,
    8,
    12,
    17,
    25,
    30,
    41,
    43,
    9,
    11,
    18,
    24,
    31,
    40,
    44,
    53,
    10,
    19,
    23,
    32,
    39,
    45,
    52,
    54,
    20,
    22,
    33,
    38,
    46,
    51,
    55,
    60,
    21,
    34,
    37,
    47,
    50,
    56,
    59,
    61,
    35,
    36,
    48,
    49,
    57,
    58,
    62,
    63,
]
# ASCII codes for CMYK, RGB
_COMMON_COMPONENT_IDS = {
    66: "B",
    67: "C",
    71: "G",
    75: "K",
    77: "M",
    82: "R",
    89: "Y",
}


def _print_app(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for an APP segment."""
    _, _, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Lp'] + 2}"
    ss = [f"\n {header:-^63} "]

    app_data = cast(bytes, sub["Ap"])
    if app_data[:5] == b"\x4a\x46\x49\x46\x00":
        # JFIF https://en.wikipendia.org/wiki/JPEG_File_Interchange_Format
        version = (app_data[5], app_data[6])
        # density units, 0: no units, 1: px/inch: 2 px/cm
        units = unpack("B", app_data[7:8])[0]
        if units == 0:
            units = "unitless"
        elif units == 1:
            units = "px/inch"
        elif units == 2:
            units = "px/cm"
        # horizontal/vertical px density
        x = unpack(">H", app_data[8:10])[0]
        y = unpack(">H", app_data[10:12])[0]
        # Thumbnail horizontal/vertical pixel count
        width, height = unpack("BB", app_data[12:14])
        # Thumbnail data
        thumbnail = app_data[14:]
        if width != 0 and height != 0:
            ss.append(
                "JFIF v{}.{}, {}, ({}, {}), {} by {} px".format(
                    *version, units, x, y, width, height
                )
            )
        else:
            ss.append("JFIF v{}.{}, no thumbnail".format(*version))

        if thumbnail:
            data = " ".join(f"{cc:02X}" for cc in thumbnail)
            for ii in range(0, len(data), 60):
                ss.append(f"  {data[ii : ii + 60]}")

    elif app_data[:6] == b"\x45\x78\x69\x66\x00\x00":
        ss.append("EXIF:")
        data = " ".join(f"{cc:02X}" for cc in app_data[6:])
        for ii in range(0, len(data), 60):
            ss.append(f"  {data[ii : ii + 60]}")
    elif app_data[:6] == b"\x41\x64\x6f\x62\x65\x00":
        # Adobe
        ss.append("Adobe v{}:".format(app_data[6]))
        data = " ".join(f"{cc:02X}" for cc in app_data[6:])
        for ii in range(0, len(data), 60):
            ss.append(f"  {data[ii : ii + 60]}")
    else:
        # Unknown
        ss.append("Unknown APP data")
        ldata = [f"{cc:02X}" for cc in app_data]
        for ii in range(0, len(ldata), 20):
            ss.append(f"  {' '.join(ldata[ii : ii + 20])}")

    return "\n".join(ss)


def _print_com(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for a COM segment."""
    _m, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Lc'] + 2}"
    ss = [f"\n {header:-^63} "]

    comment = f"'{sub['Cm'].decode('utf-8')}'"
    ss.append(f"{comment[:47]}")
    comment = comment[47:]

    while True:
        if not comment:
            break
        line = comment[:63]
        comment = comment[63:]

        ss.append(f"         {line}")

    return "\n".join(ss)


def _print_dac(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for a DAC segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['La'] + 2}"
    ss = [f"\n {header:-^63} "]
    ss.append(f"Tc={sub['Tc']}, Tb={sub['Tb']}, Cs={sub['Cs']}")

    return "\n".join(ss)


def _print_dhp(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for a DHP segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Lf'] + 2}"
    ss = [f"\n {header:-^63} "]

    ss.append(f"Sample size (px): {sub['X']} x {sub['Y']}")
    ss.append(f"Sample precision (bits): {sub['P']}")
    ss.append(f"Number of component images: {sub['Nf']}")

    for ci, vv in sub["Ci"].items():
        h, v, tqi = vv["Hi"], vv["Vi"], vv["Tqi"]
        try:
            ci = _COMMON_COMPONENT_IDS[ci]
        except KeyError:
            pass

        ss.append(f"  Component ID: {ci}")
        ss.append(f"    Horizontal sampling factor: {h}")
        ss.append(f"    Vertical sampling factor: {v}")
        ss.append(f"    Quantization table destination: {tqi}")

    return "\n".join(ss)


def _print_dht(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for a DHT segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Lh'] + 2}"
    ss = [f"\n {header:-^63} "]

    for tc, th, li in zip(sub["Tc"], sub["Th"], sub["Li"]):
        vij = sub["Vij"][(tc, th)]
        if tc == 0:
            ss.append(f"Lossless/DC Huffman, table ID: {th}")
        elif tc == 1:
            ss.append(f"AC Huffman, table ID: {th}")
        else:
            raise NotImplementedError

        ss.append("   1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16")
        nr_values = " ".join(f"{val:>02X}" for val in li)
        ss.append(f"  {nr_values} : # codes")

        for ii, (kk, values) in enumerate(vij.items()):
            if values is not None:
                for jj in range(0, len(values), 16):
                    vals = [f"{vv:>02X}" for vv in values[jj : jj + 16]]
                    ss.append(f"  {' '.join(vals):<47} : L = {kk}")

    return "\n".join(ss)


def _print_dqt(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for a DQT segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Lq'] + 2}"
    ss = [f"\n {header:-^63} "]

    for pq, tq, qk in zip(sub["Pq"], sub["Tq"], sub["Qk"]):
        ss.append(f"Table destination ID: {tq}")
        if pq == 0:
            ss.append(f"Table precision: {pq} (8-bit)")
        else:
            ss.append(f"Table precision: {pq} (16-bit)")

        new_qk = []
        for index in ZIGZAG:
            new_qk.append(qk[index])

        ss.append("Quantization table:")
        for ii in range(0, 64, 8):
            if not pq:
                # 8-bit
                table_rows = [f"{qq:>2}" for qq in new_qk[ii : ii + 8]]
            else:
                # 16-bit
                table_rows = [f"{qq:>3}" for qq in new_qk[ii : ii + 8]]

            ss.append(f"  {'  '.join(table_rows)}")

    return "\n".join(ss)


def _print_dnl(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for a DNL segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Ld'] + 2}"
    ss = [f"\n {header:-^63} "]
    ss.append(f"NL={sub['NL']}")

    return "\n".join(ss)


def _print_dri(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for a DRI segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Lr'] + 2}"
    ss = [f"\n {header:-^63} "]
    ss.append(f"Ri={sub['Ri']}")

    return "\n".join(ss)


def _print_eoi(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for an EOI segment."""
    m_bytes, fill, sub = info
    header = f"{marker} marker at offset {offset}"
    ss = [f"\n {header:-^63} "]

    return "\n".join(ss)


def _print_exp(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for an EXP segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Le'] + 2}"
    ss = [f"\n {header:-^63} "]
    ss.append(f"Eh={sub['Eh']}, Ev={sub['Ev']}")

    return "\n".join(ss)


def _print_sof(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for a SOF segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Lf'] + 2}"
    ss = [f"\n {header:-^63} "]

    sof_type = {
        0xFFC0: "Baseline sequential DCT",  # SOF0
        0xFFC1: "Extended sequential DCT, Huffman coding",  # SOF1
        0xFFC2: "Progressive DCT, Huffman coding",  # SOF2
        0xFFC3: "Lossless (sequential), Huffman coding",  # SOF3
        0xFFC5: "Differential sequential DCT, Huffman coding",  # SOF5
        0xFFC6: "Differential progressive DCT, Huffman coding",  # SOF6
        0xFFC7: "Differential lossless (sequential), Huffman coding",  # SOF7
        0xFFC9: "Extended sequential DCT, arithmetic coding",  # SOF9
        0xFFCA: "Progressive DCT, arithmetic coding",  # SOF10
        0xFFCB: "Lossless (sequential), arithmetic coding",  # SOF11
        0xFFCD: "Differential sequential DCT, arithmetic coding",  # SOF13
        0xFFCE: "Differential progressive DCT, arithmetic coding",  # SOF14
        0xFFCF: "Differential lossless (sequential), arithmetic coding",  # SOF15
    }

    try:
        ss.append(sof_type[m_bytes])
    except KeyError:
        ss.append(f"Unknown SOF type: {hex(m_bytes)}")

    ss.append(f"Sample size (px): {sub['X']} x {sub['Y']}")
    ss.append(f"Sample precision (bits): {sub['P']}")
    ss.append(f"Number of component images: {sub['Nf']}")

    for ci, vv in sub["Ci"].items():
        h, v, tqi = vv["Hi"], vv["Vi"], vv["Tqi"]
        try:
            ci = _COMMON_COMPONENT_IDS[ci]
        except KeyError:
            pass
        ss.append(f"  Component ID: {ci}")
        ss.append(f"    Horizontal sampling factor: {h}")
        ss.append(f"    Vertical sampling factor: {v}")
        ss.append(f"    Quantization table destination: {tqi}")

    return "\n".join(ss)


def _print_soi(marker: str, offset: int, info: Tuple[int, int, Dict[str, Any]]) -> str:
    """String output for a SOI segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}"
    ss = [f"\n {header:-^63} "]

    return "\n".join(ss)


def _print_sos(
    marker: str,
    offset: int,
    info: Tuple[int, int, Dict[Union[str, Tuple[str, int]], Any]],
) -> str:
    """String output for a SOS segment."""
    m_bytes, fill, sub = info

    header = f"{marker} marker at offset {offset}, length {sub['Ls'] + 2}"
    ss = [f"\n {header:-^63} "]
    ss.append(f"Number of image components: {sub['Ns']}")

    for csk, td, ta in zip(sub["Csj"], sub["Tdj"], sub["Taj"]):
        try:
            csk = _COMMON_COMPONENT_IDS[csk]
        except KeyError:
            pass
        ss.append(f"  Component: {csk}, DC table: {td}, AC table: {ta}")

    ss.append(f"Spectral selectors start-end: {sub['Ss']}-{sub['Se']}")
    ss.append(f"Successive approximation bit high-low: {sub['Ah']}-{sub['Al']}")

    # Write RST and encoded data lengths
    remove = ["Ls", "Ns", "Csj", "Tdj", "Taj", "Ss", "Se", "Ah", "Al"]
    keys = [kk for kk in sub if kk not in remove]
    for key in keys:
        if key[0] == "ENC":
            ss.append(f"\n{' ENC marker at offset {key[1]}':.^63}")
            ss.append(f"\n{len(sub[key])} bytes of entropy-coded data")
        else:
            (name, offset) = cast(Tuple[str, int], key)
            ss.append(f"{offset:<7}{name}(FFD{name[-1]})")

    return "\n".join(ss)


PRINTERS = {
    "APP": _print_app,
    "COM": _print_com,
    "DAC": _print_dac,
    "DHP": _print_dhp,
    "DHT": _print_dht,
    "DQT": _print_dqt,
    "DNL": _print_dnl,
    "DRI": _print_dri,
    "EOI": _print_eoi,
    "EXP": _print_exp,
    "SOF": _print_sof,
    "SOI": _print_soi,
    "SOS": _print_sos,
}
