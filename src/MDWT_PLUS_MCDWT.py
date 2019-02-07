#!/usr/bin/env python

# Note: swap the above line with the following two ones to switch
# between the standar and the optimized mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

# import cv2
# import numpy as np
# import pywt
# import math

#import cv2
import numpy as np
import sys
import os

from MDWT import MDWT
from MCDWT import MCDWT
sys.path.insert(0, "..")
from src.IO import decomposition

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
#        "  yes | cp -rf ../sequences/stockholm/ /tmp/\n"
    parser = argparse.ArgumentParser(
        description = "Motion 2D Discrete Wavelet (color) Transform + Motion Compensated 2D Discrete Wavelet (color) Transform\n\n"
        "Examples:\n\n"
        "  rm -rf /tmp/stockholm/\n"
        "  cp -r ../sequences/stockholm/ /tmp/\n"
        "  python3 -O ./MDWT_PLUS_MCDWT.py    -i ../sequences/stockholm/ -d /tmp/stockholm_ -m /tmp/mc_stockholm_ # Forward transform\n",
        formatter_class=CustomFormatter)

    parser.add_argument("-i", "--images",
                        help="Sequence of images", default="/tmp/stockholm/")

    parser.add_argument("-d", "--decompositions",
                        help="Sequence of decompositions", default="/tmp/stockholm_")

    parser.add_argument("-N",
                        help="Number of images/decompositions", default=5, type=int)

    parser.add_argument("-m", "--mc_decompositions",
                        help="Sequence of motion compensated decompositions", default="/tmp/mc_stockholm_")

    parser.add_argument("-T",
                        help="Number of temporal levels", default=2, type=int)

    parser.add_argument("-K",
                        help="Number of spatial levels", default=2, type=int)

    args = parser.parse_args()
    path = os.path.dirname(args.decompositions)

    '''Execute MDWT + MCDWT K times'''
    for i in range(args.K):
        '''MDWT Transform'''
        d = MDWT()
        p = d.forward(args.images, args.decompositions, args.N)

        '''MCDWT Transform'''
        p = decomposition.readL("{}000".format(args.decompositions))
        d = MCDWT(p.shape)
        p = d.forward(args.decompositions, args.decompositions, args.N, args.T)

        path += '/LL/'
        args.decompositions = path + os.path.basename(decompositions)
        args.images = args.decompositions