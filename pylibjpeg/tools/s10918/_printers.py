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


ZIGZAG = [
     0,  1,  5,  6, 14, 15, 27, 28,
     2,  4,  7, 13, 16, 26, 29, 42,
     3,  8, 12, 17, 25, 30, 41, 43,
     9, 11, 18, 24, 31, 40, 44, 53,
    10, 19, 23, 32, 39, 45, 52, 54,
    20, 22, 33, 38, 46, 51, 55, 60,
    21, 34, 37, 47, 50, 56, 59, 61,
    35, 36, 48, 49, 57, 58, 62, 63
]
# ASCII codes for CMYK, RGB
_COMMON_COMPONENT_IDS = {
    66 : 'B', 67 : 'C', 71 : 'G', 75 : 'K', 77 : 'M', 82 : 'R',
    89 : 'Y',
}


def _print_app(marker, offset, info):
    """String output for an APP segment."""
    _, _, info = info

    ss = []
    ss.append(
        '\n{:-^63}'.format(' {} marker at offset {}, length {} '
        .format(marker, offset, info['Lp'] + 2))
    )

    app_data = info['Ap']
    if app_data[:5] == b'\x4a\x46\x49\x46\x00':
        # JFIF https://en.wikipendia.org/wiki/JPEG_File_Interchange_Format
        version = (app_data[5], app_data[6])
        # density units, 0: no units, 1: px/inch: 2 px/cm
        units = unpack('B', app_data[7:8])[0]
        if units == 0:
            units = 'unitless'
        elif units == 1:
            units = 'px/inch'
        elif units == 2:
            units = 'px/cm'
        # horizontal/vertical px density
        x = unpack('>H', app_data[8:10])[0]
        y = unpack('>H', app_data[10:12])[0]
        # Thumbnail horizontal/vertical pixel count
        width, height = unpack('BB', app_data[12:14])
        # Thumbnail data
        thumbnail = app_data[14:]
        if width != 0 and height != 0:
            ss.append(
                'JFIF v{}.{}, {}, ({}, {}), {} by {} px'
                .format(*version, units, x, y, width, height)
            )
        else:
            ss.append('JFIF v{}.{}, no thumbnail'.format(*version))

        if thumbnail:
            data = ' '.join(['{:02x}'.format(cc) for cc in thumbnail])
            for ii in range(0, len(data), 60):
                ss.append('  {}'.format(data[ii:ii + 60]))

    elif app_data[:6] == b'\x45\x78\x69\x66\x00\x00':
        ss.append('EXIF:')
        data = ' '.join(['{:02x}'.format(cc) for cc in app_data[6:]])
        for ii in range(0, len(data), 60):
            ss.append('  {}'.format(data[ii:ii + 60]))
    elif app_data[:6] == b'\x41\x64\x6f\x62\x65\x00':
        # Adobe
        ss.append('Adobe v{}:'.format(app_data[6]))
        data = ' '.join(['{:02x}'.format(cc) for cc in app_data[6:]])
        for ii in range(0, len(data), 60):
            ss.append('  {}'.format(data[ii:ii + 60]))
    else:
        # Unknown
        ss.append('Unknown APP data')
        data = ['{:02x}'.format(cc) for cc in app_data]
        for ii in range(0, len(data), 20):
            ss.append('  {}'.format(' '.join(data[ii:ii + 20])))

    return '\n'.join(ss)


def _print_com(marker, offset, info):
    """String output for a COM segment."""
    _m, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(' {} marker at offset {}, length {} '
        .format(marker, offset, info['Lc'] + 2))
    )

    comment = "'" + info['Cm'].decode('utf-8') + "'"
    ss.append("{}".format(comment[:47]))
    comment = comment[47:]

    while True:
        if not comment:
            break
        line = comment[:63]
        comment = comment[63:]

        ss.append("         {}".format(line))

    return '\n'.join(ss)


def _print_dac(marker, offset, info):
    """String output for a DAC segment."""
    m_bytes, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(
            ' {} marker at offset {}, length {} '
            .format(marker, offset, info['La'] + 2)
        )
    )
    ss.append(
        "Tc={}, Tb={}, Cs={}".format(info['Tc'], info['Tb'], info['Cs'])
    )

    return '\n'.join(ss)


def _print_dhp(marker, offset, info):
    """String output for a DHP segment."""
    m_bytes, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(' {} marker at offset {}, length {} '
        .format(marker, offset, info['Lf'] + 2))
    )

    ss.append('Sample size (px): {} x {}'.format(info['X'], info['Y']))
    ss.append('Sample precision (bits): {}'.format(info['P']))
    ss.append('Number of component images: {}'.format(info['Nf']))

    for ci, vv in info['Ci'].items():
        h, v, tqi = vv['Hi'], vv['Vi'], vv['Tqi']
        try:
            ci = _COMMON_COMPONENT_IDS[ci]
        except KeyError:
            pass
        ss.append('  Component ID: {}'.format(ci))
        ss.append('    Horizontal sampling factor: {}'.format(h))
        ss.append('    Vertical sampling factor: {}'.format(v))
        ss.append('    Quantization table destination: {}'.format(tqi))

    return '\n'.join(ss)


def _print_dht(marker, offset, info):
    """String output for a DHT segment."""
    _m, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(' {} marker at offset {}, length {} '
        .format(marker, offset, info['Lh'] + 2))
    )

    for tc, th, li in zip(info['Tc'], info['Th'], info['Li']):
        vij = info['Vij'][(tc, th)]
        if tc == 0:
            ss.append('Lossless/DC Huffman, table ID: {}'.format(th))
        elif tc == 1:
            ss.append('AC Huffman, table ID: {}'.format(th))
        else:
            raise NotImplementedError

        ss.append('   1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16')
        nr_values = ' '.join(['{:>02x}'.format(val) for val in li])
        ss.append('  {} : # codes'.format(nr_values))

        for ii, (kk, values) in enumerate(vij.items()):
            if values is not None:
                for jj in range(0, len(values), 16):
                    vals = ['{:>02x}'.format(vv) for vv in values[jj:jj + 16]]
                    val = ' '.join(vals)
                    ss.append('  {:<47} : L = {}'.format(val, kk))

    return '\n'.join(ss)


def _print_dqt(marker, offset, info):
    """String output for a DQT segment."""
    _m, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(' {} marker at offset {}, length {} '
        .format(marker, offset, info['Lq'] + 2))
    )
    for pq, tq, qk in zip(info['Pq'], info['Tq'], info['Qk']):
        ss.append('Table destination ID: {}'.format(tq))
        if pq == 0:
            ss.append('Table precision: {} (8-bit)'.format(pq))
        else:
            ss.append('Table precision: {} (16-bit)'.format(pq))

        new_qk = []
        for index in ZIGZAG:
            new_qk.append(qk[index])

        ss.append('Quantization table:')
        for ii in range(0, 64, 8):
            if not pq:
                # 8-bit
                table_rows = ['{:>2}'.format(qq) for qq in new_qk[ii:ii + 8]]
            else:
                # 16-bit
                table_rows = ['{:>3}'.format(qq) for qq in new_qk[ii:ii + 8]]

            ss.append('  {}'.format('  '.join(table_rows)))

    return '\n'.join(ss)


def _print_dnl(marker, offset, info):
    """String output for a DNL segment."""
    m_bytes, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(
            ' {} marker at offset {}, length {} '
            .format(marker, offset, info['Ld'] + 2)
        )
    )
    ss.append("NL={}".format(info['NL']))

    return '\n'.join(ss)


def _print_dri(marker, offset, info):
    """String output for a DRI segment."""
    m_bytes, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(' {} marker at offset {}, length {} '
        .format(marker, offset, info['Lr'] + 2))
    )
    ss.append(
        "Ri={}".format(info['Ri'])
    )
    return '\n'.join(ss)


def _print_eoi(marker, offset, info):
    """String output for an EOI segment."""
    return (
        '\n{:=^63}'.format(' {} marker at offset {} '.format(marker, offset))
    )


def _print_exp(marker, offset, info):
    """String output for an EXP segment."""
    m_bytes, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(
            ' {} marker at offset {}, length {} '
            .format(marker, offset, info['Le'] + 2)
        )
    )
    ss.append("Eh={}, Ev={}".format(info['Eh'], info['Ev']))

    return '\n'.join(ss)


def _print_sof(marker, offset, info):
    """String output for a SOF segment."""
    m_bytes, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(' {} marker at offset {}, length {} '
        .format(marker, offset, info['Lf'] + 2))
    )

    sof_type = {
        0xFFC0: 'Baseline sequential DCT',  # SOF0
        0xFFC1: 'Extended sequential DCT, Huffman coding',  # SOF1
        0xFFC2: 'Progressive DCT, Huffman coding',  # SOF2
        0xFFC3: 'Lossless (sequential), Huffman coding',  # SOF3
        0xFFC5: 'Differential sequential DCT, Huffman coding',  # SOF5
        0xFFC6: 'Differential progressive DCT, Huffman coding',  # SOF6
        0xFFC7: 'Differential lossless (sequential), Huffman coding',  # SOF7
        0xFFC9: 'Extended sequential DCT, arithmetic coding',  # SOF9
        0xFFCA: 'Progressive DCT, arithmetic coding',  # SOF10
        0xFFCB: 'Lossless (sequential), arithmetic coding',  # SOF11
        0xFFCD: 'Differential sequential DCT, arithmetic coding',  # SOF13
        0xFFCE: 'Differential progressive DCT, arithmetic coding',  # SOF14
        0xFFCF: 'Differential lossless (sequential), arithmetic coding',  # SOF15
    }

    try:
        ss.append('{}'.format(sof_type[m_bytes]))
    except KeyError:
        ss.append('Unknown SOF type: {}'.format(hex(m_bytes)))

    ss.append('Sample size (px): {} x {}'.format(info['X'], info['Y']))
    ss.append('Sample precision (bits): {}'.format(info['P']))
    ss.append('Number of component images: {}'.format(info['Nf']))

    for ci, vv in info['Ci'].items():
        h, v, tqi = vv['Hi'], vv['Vi'], vv['Tqi']
        try:
            ci = _COMMON_COMPONENT_IDS[ci]
        except KeyError:
            pass
        ss.append('  Component ID: {}'.format(ci))
        ss.append('    Horizontal sampling factor: {}'.format(h))
        ss.append('    Vertical sampling factor: {}'.format(v))
        ss.append('    Quantization table destination: {}'.format(tqi))

    return '\n'.join(ss)


def _print_soi(marker, offset, info):
    """String output for a SOI segment."""
    return '\n{:=^63}'.format(' {} marker at offset {} '.format(marker, offset))


def _print_sos(marker, offset, info):
    """String output for a SOS segment."""
    _m, fill, info = info
    ss = []
    ss.append(
        '\n{:-^63}'.format(' {} marker at offset {}, length {} '
        .format(marker, offset, info['Ls'] + 2))
    )
    ss.append("Number of image components: {}".format(info['Ns']))

    for csk, td, ta in zip(info['Csj'], info['Tdj'], info['Taj']):
        try:
            csk = _COMMON_COMPONENT_IDS[csk]
        except KeyError:
            pass
        ss.append(
            '  Component: {}, DC table: {}, AC table: {}'.format(csk, td, ta)
        )

    ss.append(
        'Spectral selectors start-end: {}-{}'.format(info['Ss'], info['Se'])
    )
    ss.append(
        'Successive approximation bit high-low: {}-{}'
        .format(info['Ah'], info['Al'])
    )

    # Write RST and encoded data lengths
    remove = ['Ls', 'Ns', 'Csj', 'Tdj', 'Taj', 'Ss', 'Se', 'Ah', 'Al']
    keys = [kk for kk in info if kk not in remove]
    for key in keys:
        if key[0] == 'ENC':
            ss.append(
                '\n{:.^63}'.format(' ENC marker at offset {}'.format(key[1]))
            )
            ss.append(
                '\n{} bytes of entropy-coded data'.format(len(info[key]))
            )
        else:
            (name, offset) = key
            ss.append(
                '{:<7}{}({})'.format(offset, name, 'ffd{}'.format(name[-1]))
            )

    return '\n'.join(ss)


PRINTERS = {
    'APP' : _print_app,
    'COM' : _print_com,
    'DAC' : _print_dac,
    'DHP' : _print_dhp,
    'DHT' : _print_dht,
    'DQT' : _print_dqt,
    'DNL' : _print_dnl,
    'DRI' : _print_dri,
    'EOI' : _print_eoi,
    'EXP' : _print_exp,
    'SOF' : _print_sof,
    'SOI' : _print_soi,
    'SOS' : _print_sos,
}
