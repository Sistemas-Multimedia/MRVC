#!/usr/bin/env python

# Note: swap the above line with the following two ones to switch
# between the standard and the optimized mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

import numpy as np
import sys

from DWT import DWT
sys.path.insert(0, "..")
from IO import decomposition

class MCDWT:

    def __init__(self, shape):
        self.zero_L = np.zeros(shape, np.float64)
        self.zero_H = (np.zeros(shape, np.float64), np.zeros(shape, np.float64), np.zeros(shape, np.float64))
        self.dwt = DWT()

    def __forward_butterfly(self, aL, aH, bL, bH, cL, cH):
        AL = self.dwt.backward((aL, self.zero_H))
        BL = self.dwt.backward((bL, self.zero_H))
        CL = self.dwt.backward((cL, self.zero_H))
        AH = self.dwt.backward((self.zero_L, aH))
        BH = self.dwt.backward((self.zero_L, bH))
        CH = self.dwt.backward((self.zero_L, cH))
        prediction_BH  = predictor.generate_prediction(AL, BL, CL, AH, CH)
        residue_BH = BH - prediction_BH
        residue_bH = self.dwt.forward(residue_BH)
        return residue_bH[1]

    def __backward_butterfly(self, aL, aH, bL, residue_bH, cL, cH):
        AL = self.dwt.backward((aL, self.zero_H))
        BL = self.dwt.backward((bL, self.zero_H))
        CL = self.dwt.backward((cL, self.zero_H))
        AH = self.dwt.backward((self.zero_L, aH))
        residue_BH = self.dwt.backward((self.zero_L, residue_bH))
        CH = self.dwt.backward((self.zero_L, cH))
        prediction_BH  = predictor.generate_prediction(AL, BL, CL, AH, CH)
        BH = residue_BH + prediction_BH
        bH = self.dwt.forward(BH)
        return bH[1]

    def forward(self, prefix = "/tmp/", N=5, T=2):
        x = 2
        for t in range(T): # Temporal scale
            i = 1
            aL, aH = decomposition.read(prefix, "{:04d}".format(0))
            while i < (N//x):
                bL, bH = decomposition.read(prefix, "{:04d}".format(x*i+x//2))
                cL, cH = decomposition.read(prefix, "{:04d}".format(x*i+x))
                residue_bH = self.__forward_butterfly(aL, aH, bL, bH, cL, cH)
                decomposition.writeH(residue_bH, prefix, "{:04d}".format(x*i+x//2))
                aL, aH = cL, cH
                i += 1
            x *= 2

    def backward(self, prefix = "/tmp/", N=5, T=2):
        x = 2**T
        for t in range(T): # Temporal scale
            i = 0
            aL, aH = decomposition.read(prefix, "{:03d}".format(0))
            while i < (N//x):
                bL, residue_bH = decomposition.read(prefix, "{:03d}".format(x*i+x//2))
                cL, cH = decomposition.read(prefix, "{:03d}".format(x*i+x))
                bH = self.__backward_butterfly(aL, aH, bL, residue_bH, cL, cH)
                decomposition.writeH(bH, prefix, "{:03d}".format(x*i+x//2))
                aL, aH = cL, cH
                i += 1
            x //=2

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

#        "  yes | cp -rf ../sequences/stockholm/ /tmp/\n"
    parser = argparse.ArgumentParser(
        description = "Motion Compensated 2D Discrete Wavelet Transform\n\n"
        "Example:\n\n"
        "  yes | cp ../sequences/stockholm/* /tmp/\n"
        "  python3 -O MDWT.py     -p /tmp/\n"
        "  python3 -O MCDWT.py    -p /tmp/\n"
        "  python3 -O MCDWT.py -b -p /tmp/\n"
        "  python3 -O MDWT.py  -b -p /tmp/\n",
        formatter_class=CustomFormatter)

    parser.add_argument("-b", "--backward", action='store_true', help="Performs backward transform")
    parser.add_argument("-p", "--prefix", help="Dir where the files the I/O files are placed", default="/tmp/")
    parser.add_argument("-N", "--decompositions", help="Number of input decompositions", default=5, type=int)
    parser.add_argument("-T", "--iterations", help="Number of temporal iterations", default=2, type=int)
    parser.add_argument("-P", "--predictor", help="Predictor to use (0=none, 1=MC average, 2=MC weighted average, 3=left, 4=right, 5=MC left, 6=MC right, 7=offset)", default=1, type=int)

    args = parser.parse_args()

    if args.predictor == 0:
        import no_prediction as predictor
    if args.predictor == 1:
        import simple_average as predictor
    if args.predictor == 2:
        import weighted_average as predictor
    if args.predictor == 3:
        import left_prediction as predictor
    if args.predictor == 4:
        import right_prediction as predictor
    if args.predictor == 5:
        import left_MC_prediction as predictor
    if args.predictor == 6:
        import right_MC_prediction as predictor
    if args.predictor == 7:
        import offset_prediction as predictor

    if args.backward:
        if __debug__:
            print("Backward transform")

        # The first image is read only for knowing the dimenssions of
        # the images.
        p = decomposition.readL(args.prefix, "000")
        d = MCDWT(p.shape)

        d.backward(args.prefix, args.decompositions, args.iterations)
    else:
        if __debug__:
            print("Forward transform")

        p = decomposition.readL(args.prefix, "0001")
        d = MCDWT(p.shape)

        p = d.forward(args.prefix, args.decompositions, args.iterations)
