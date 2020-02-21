#!/usr/bin/env python

import os
from pyjpeg import decode


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    infile = bytes(os.path.join(SCRIPT_DIR, 'in.jpg'), 'utf-8')
    outfile = bytes(os.path.join(SCRIPT_DIR, 'out.pnm'), 'utf-8')

    decode(infile, outfile)
