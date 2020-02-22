
import _libjpeg


def decode(infile, outfile, nr_bytes):
    return _libjpeg.decode(infile, outfile, nr_bytes)
