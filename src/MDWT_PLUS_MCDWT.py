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

from DWT import DWT
sys.path.insert(0, "..")
from src.IO import image
from src.IO import decomposition
from MC.optical.motion import generate_prediction

class MDWT:

    def __init__(self):
        self.dwt = DWT()

    def forward(self, s="/tmp/stockholm/", S="/tmp/stockholm_", N=5, iteration=0):
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
            if iteration != 0:
                img = decomposition.readL("{}{:03d}".format(s, i))
            else:
                img = image.read("{}{:03d}".format(s, i))
            pyr = self.dwt.forward(img)
            decomposition.write(pyr, "{}{:03d}".format(S, i))

class MCDWT:

    def __init__(self, shape):
        self.zero_L = np.zeros(shape, np.float64)
        self.zero_H = (self.zero_L, self.zero_L, self.zero_L)
        self.dwt = DWT()

    def __forward_butterfly(self, aL, aH, bL, bH, cL, cH):
        '''Motion compensated forward MCDWT butterfly.
        Input:
        -----
        aL, aH, bL, bH, cL, cH: array[y, x, component], the decomposition of
        the images a, b and c.
        Output:
        ------
        residue_bH: array[y, x, component], the base of the decomposition of
        the residue fot the image b.
        '''

        AL = self.dwt.backward((aL, self.zero_H))
        BL = self.dwt.backward((bL, self.zero_H))
        CL = self.dwt.backward((cL, self.zero_H))
        AH = self.dwt.backward((self.zero_L, aH))
        BH = self.dwt.backward((self.zero_L, bH))
        CH = self.dwt.backward((self.zero_L, cH))
        BHA = generate_prediction(AL, BL, AH)
        BHC = generate_prediction(CL, BL, CH)
        prediction_BH = (BHA + BHC) / 2
        residue_BH = BH - prediction_BH
        residue_bH = self.dwt.forward(residue_BH)
        return residue_bH[1]

    def forward(self, s="/tmp/stockholm_", S="/tmp/mc_stockholm_", N=5, T=2):
        '''A Motion Compensated Discrete Wavelet Transform.
        Compute the MC 1D-DWT. The input video s (as a sequence of
        1-levels decompositions) must be stored in disk and the output (as a
        1-levels MC decompositions) will be stored in S.
        Imput:
        -----
            prefix : s
                Localization of the input images. Example: "/tmp/stockholm_".
             N : int
                Number of images to process.
             T : int
                Number of levels of the MCDWT (temporal scales). Controls
                the GOP size.
                  T | GOP_size
                ----+-----------
                  0 |        1
                  1 |        2
                  2 |        4
                  3 |        8
                  4 |       16
                  5 |       32
                  : |        :
        Returns
        -------
            prefix : S
                Localization of the output decompositions. For example:
                "/tmp/mc_stockholm_".
        '''
        x = 2
        for t in range(T): # Temporal scale
            i = 0
            aL, aH = decomposition.read("{}{:03d}".format(s, 0))
            decomposition.write((aL, aH), "{}{:03d}".format(S, 0))
            while i < (N//x):
                bL, bH = decomposition.read("{}{:03d}".format(s, x*i+x//2))
                cL, cH = decomposition.read("{}{:03d}".format(s, x*i+x))
                bH = self.__forward_butterfly(aL, aH, bL, bH, cL, cH)
                decomposition.write((bL, bH), "{}{:03d}".format(S, x*i+x//2))
                decomposition.write((cL, cH), "{}{:03d}".format(S, x*i+x))
                aL, aH = cL, cH
                i += 1
            x *= 2

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

    '''Execute MDWT + MCDWT K times'''
    for i in range(args.K):
        '''MDWT Transform'''
        d = MDWT()
        p = d.forward(args.images, args.decompositions, args.N, i)
        args.images = args.decompositions

        '''MCDWT Transform'''
        p = decomposition.readL("{}000".format(args.decompositions))
        d = MCDWT(p.shape)
        p = d.forward(args.decompositions, args.decompositions, args.N, args.T)
