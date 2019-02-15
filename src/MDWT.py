#!/usr/bin/env python

# Note: swap the above line with the following two ones to switch
# between the standar and the optimized mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

import sys

from DWT import DWT
sys.path.insert(0, "..")
from src.IO import image
from src.IO import decomposition

class MDWT:

    def __init__(self):
        self.dwt = DWT()

    def forward(self, prefix="/tmp/", N=5):
        '''Motion 1-iteration forward 2D DWT of a sequence of images.

        Compute the forward 2D-DWT of each image of the sequence
        placed at <prefix>.

        Input
        -----

            prefix: the sequence of images to be transformed.
            N: number of images.

        Output
        ------

            (disk): the sequence of decompositions.

        '''
        for i in range(N):
            img = image.read(prefix, "{:03d}".format(i))
            pyr = self.dwt.forward(img)
            decomposition.write(pyr, prefix, "{:03d}".format(i))

    def backward(self, prefix="/tmp/", N=5):
        '''Motion 1-iteration forward 2D DWT of a sequence of decompositions.

        Compute the inverse 2D-DWT of each decomposition of the
        sequence of decompositions placed at <prefix>.

        Input:
        -----

            prefix: the sequence of decompositions to be transformed.
            N: the number of decompositions.

        Output:
        ------

            (disk): the sequence of images.

        '''

        for i in range(N):
            pyr = decomposition.read(prefix, "{:03d}".format(i))
            img = self.dwt.backward(pyr)
            image.write(img, prefix, "{:03d}".format(i))

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
    parser = argparse.ArgumentParser(
        description = "Motion 2D Discrete Wavelet (color) Transform\n\n"
        "Examples:\n\n"
        "  yes | cp ../sequences/stockholm/* /tmp/\n"
        "  python3 -O MDWT.py    -p /tmp/ # Forward transform\n"
        "  python3 -O MDWT.py -b -p /tmp/ # Backward transform\n",
        formatter_class=CustomFormatter)

    parser.add_argument("-b", "--backward", action='store_true', help="Performs backward transform")
    parser.add_argument("-p", "--prefix", help="Dir where the files the I/O files are placed", default="/tmp/")
    parser.add_argument("-N", help="Number of images/decompositions", default=5, type=int)

    args = parser.parse_args()

    d = MDWT()
    if args.backward:
        if __debug__:
            print("Backward transform")
        d.backward(args.prefix, args.N)
    else:
        if __debug__:
            print("Forward transform")
        p = d.forward(args.prefix, args.N)
