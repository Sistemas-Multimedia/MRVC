#!/usr/bin/env python

import numpy as np
import sys

from DWT import DWT
sys.path.insert(0, "..")
from src.IO import decomposition

class MCDWT:

    def __init__(self, shape):
        self.zero_L = np.zeros(shape, np.float64)
        self.zero_H = (self.zero_L, self.zero_L, self.zero_L)
        self.dwt = DWT()

		
	def __distorsion_predictions():
	
	
	
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
        '''A Motion Compensated Discrete Wavelet Transform.

        Compute the MC 1D-DWT. The input video (as a sequence of
        1-levels decompositions) must be stored in disk in the
        directory <prefix>, and the output (as a 1-levels MC
        decompositions) will generated in the same directory.

        Input
        -----

            prefix : str

                Localization of the input/output images. Example:
                "/tmp/".

             N : int

                Number of decompositions to process.

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

             P : int

                Predictor to use:

                 1 --> Average Predictor.
                 2 --> Weighted Average Predictor.

        Returns
        -------

            None.

        '''
        x = 2
        for t in range(T): # Temporal scale
            i = 0
            aL, aH = decomposition.read(prefix, "{:03d}".format(0))
            while i < (N//x):
                bL, bH = decomposition.read(prefix, "{:03d}".format(x*i+x//2))
                cL, cH = decomposition.read(prefix, "{:03d}".format(x*i+x))
                bH = self.__forward_butterfly(aL, aH, bL, bH, cL, cH)
                decomposition.writeH(bH, prefix, "{:03d}".format(x*i+x//2))
                aL, aH = cL, cH
                i += 1
            x *= 2

    def backward(self, prefix = "/tmp/", N=5, T=2):
        x = 2**T
        for t in range(T): # Temporal scale
            i = 0
            aL, aH = decomposition.read(prefix, "{:03d}".format(0))
            while i < (N//x):
                bL, bH = decomposition.read(prefix, "{:03d}".format(x*i+x//2))
                cL, cH = decomposition.read(prefix, "{:03d}".format(x*i+x))
                bH = self.__backward_butterfly(aL, aH, bL, bH, cL, cH)
                decomposition.writeH(bH, "{:03d}".format(x*i+x//2))
                aL, aH = cL, cH
                i += 1
            x //=2

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

#        "  yes | cp -rf ../sequences/stockholm/ /tmp/\n"
    parser = argparse.ArgumentParser(
        description = "Motion Compensated 2D Discrete Wavelet (color) Transform\n\n"
        "Example:\n\n"
        "  yes | cp ../sequences/stockholm/* /tmp/\n"
        "  python3 -O MDWT.py     -p /tmp/\n"
        "  python3 -O MCDWT.py    -p /tmp/\n"
        "  python3 -O MCDWT.py -b -p /tmp/\n"
        "  python3 -O MDWT.py  -b -p /tmp/\n",
        formatter_class=CustomFormatter)

    parser.add_argument("-b", "--backward", action='store_true', help="Performs backward transform")
    parser.add_argument("-p", "--prefix", help="Dir where the files the I/O files are placed", default="/tmp/")
    parser.add_argument("-N", help="Number of decompositions", default=5, type=int)
    parser.add_argument("-T", help="Number of temporal levels", default=2, type=int)
    parser.add_argument("-P", help="Predictor to use (1=average, 2=weighted_average)", default=1, type=int)

    args = parser.parse_args()

    if args.P == 1:
        import simple_average as predictor
    else:
        import weighted_average as predictor

    if args.backward:
        if __debug__:
            print("Backward transform")

        p = decomposition.readL(args.prefix, "000")
        d = MCDWT(p.shape)

        d.backward(args.prefix, args.N, args.T)
    else:
        if __debug__:
            print("Forward transform")

        p = decomposition.readL(args.prefix, "000")
        d = MCDWT(p.shape)

        p = d.forward(args.prefix, args.N, args.T)
