#!/usr/bin/env python

# Note: swap the above line with the following two ones to switch
# between the standar and the optimized mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

import sys
import os
import math
import numpy as np
from MDWT import MDWT
sys.path.insert(0, "..")
from src.IO import decomposition

def HHtoBlack(path, N):
    for i in range(N):

        LH, HL, HH = decomposition.readH(path, "{:03d}".format(i))
        LL = decomposition.readL(path, "{:03d}".format(i))

        y = math.ceil(HH.shape[0]/2)
        x = math.ceil(HH.shape[1]/2)

        HH = HH * 0
        HH[x][y][0] = 255
        HH[x][y][1] = 255
        HH[x][y][2] = 255

        decomposition.writeH([LH,HL,HH],"{:03d}".format(i))

def getContribution(path, N):
    for i in range(N):

        LH, HL, HH = decomposition.readH(path, "{:03d}".format(i))
        LL = decomposition.readL(path, "{:03d}".format(i))

        '''CALCULATE THE CONTRIBUTION OF EACH SUBBAND'''
        print("LL Contribution --> {}\n".format(np.sum(LL*LL)/np.sum(HH*HH)))
        print("HL Contribution --> {}\n".format(np.sum(HL*HL)/np.sum(HH*HH)))
        print("LH Contribution --> {}\n\n".format(np.sum(LH*LH)/np.sum(HH*HH)))


if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
    parser = argparse.ArgumentParser(
        description = "Wavelet Contribution Calculator\n\n"
        "Example:\n\n"
        "  python3 -O ./WCONTRIBUTION.py -d /tmp/stockholm_ \n",
        formatter_class=CustomFormatter)

    parser.add_argument("-d", "--decompositions",
                        help="Sequence of decompositions", default="/tmp/stockholm_")

    parser.add_argument("-N",
                        help="Number of images/decompositions", default=5, type=int)

    args = parser.parse_args()
    path = os.path.dirname(args.decompositions)

    '''FIRST DIRECT TRANSFORM'''
    d = MDWT()
    d.forward(args.decompositions, args.N)

    '''MODIFY THE SUBBAND HH, WHITE DOT IN THE MIDDLE OF THE IMAGE AND THE REST OF PIXELS TO BLACK'''
    HHtoBlack(args.decompositions, args.N)
   

    '''RECONSTRUCT THE IMAGE AND ANOTHER DECOMPOSITION TO GET THE CONTRUBITON OF EACH SUBBAND'''
    d.backward(args.decompositions, args.N)
    d.forward(args.decompositions, args.N)

    '''GET THE CONTRUBITON OF EACH SUBBAND'''
    getContribution(args.decompositions, args.N)