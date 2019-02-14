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
import os

class MDWT:

    def __init__(self):
        self.dwt = DWT()

    def forward(self, s="../stockholm/", S="/tmp/stockholm/", N=5):
        ''' Motion 1-iteration forward 2D DWT of a sequence of images.

        Compute the 2D-DWT of each image of the sequence s.

        Input:
        -----

            s: the sequence of images to be transformed.

        Output:
        ------

            S: the sequence of decompositions (transformed images).

        '''
        for i in range(N):
            img = image.read(s, "{:03d}".format(i), ".png")
            pyr = self.dwt.forward(img)
            #dir_name = "{}{:03d}".format(S, i)
            #print("dir_name=",dir_name)
            #os.mkdir(dir_name)
            decomposition.write(pyr, S, "{:03d}".format(i), ".png")

    def backward(self, S="/tmp/stockholm/", s="/tmp/", N=5):
        ''' Motion 1-iteration forward 2D DWT of a sequence of decompositions.

        Compute the inverse 2D-DWT of each decomposition of the sequence S.

        Input:
        -----

            S: the sequence of decompositions to be transformed.

        Output:
        ------

            s: the sequence of images.

        '''

        for i in range(N):
            pyr = decomposition.read("{}{:03d}/".format(S, i))
            img = self.dwt.backward(pyr)
            image.write(img, "{}{:03d}".format(s, i))

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
    parser = argparse.ArgumentParser(
        description = "Motion 2D Discrete Wavelet (color) Transform\n\n"
        "Examples:\n\n"
        "  rm -rf /tmp/stockholm/\n"
        "  cp -r ../sequences/stockholm/ /tmp/\n"
        "  ./MDWT.py    -i /tmp/stockholm/ -d /tmp/stockholm_ # Forward transform\n"
        "  ./MDWT.py -b -i /tmp/stockholm_ -d /tmp/stockholm_ # Backward transform\n",
        formatter_class=CustomFormatter)

    parser.add_argument("-b", "--backward", action='store_true',
                        help="Performs backward transform")

    parser.add_argument("-i", "--images",
                        help="Sequence of images", default="/tmp/")

    parser.add_argument("-d", "--decompositions",
                        help="Sequence of decompositions", default="/tmp/")

    parser.add_argument("-N",
                        help="Number of images/decompositions", default=5, type=int)

    args = parser.parse_args()

    d = MDWT()
    if args.backward:
        if __debug__:
            print("Backward transform")
        d.backward(args.decompositions, args.images, args.N)
    else:
        if __debug__:
            print("Forward transform")
        p = d.forward(args.images, args.decompositions, args.N)
