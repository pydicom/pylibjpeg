
import _libjpeg


def decode(infile, outfile):
    return _libjpeg.decode(infile, outfile)
