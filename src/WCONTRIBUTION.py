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
from DWT import DWT
sys.path.insert(0, "..")
from src.IO import decomposition

def getLLContribution(path, N):
    d = DWT()
    for i in range(N):

        LL, LH, HL, HH = LLtoBlack(path, N)
        imgLL = d.backward((LL, (LH, HL, HH)))

        LL, LH, HL, HH = HHtoBlack(path, N)
        imgHH = d.backward((LL, (LH, HL, HH)))

        print("LL Contribution --> {}\n".format(np.sum(imgLL*imgLL)/np.sum(imgHH*imgHH)))

def getHLContribution(path, N):
    d = DWT()
    for i in range(N):

        LL, LH, HL, HH = HLtoBlack(path, N)
        imgHL = d.backward((LL, (LH, HL, HH)))

        LL, LH, HL, HH = HHtoBlack(path, N)
        imgHH = d.backward((LL, (LH, HL, HH)))

        print("HL Contribution --> {}\n".format(np.sum(imgHL*imgHL)/np.sum(imgHH*imgHH)))

def getLHContribution(path, N):
    d = DWT()
    for i in range(N):

        LL, LH, HL, HH = LHtoBlack(path, N)
        imgLH = d.backward((LL, (LH, HL, HH)))

        LL, LH, HL, HH = HHtoBlack(path, N)
        imgHH = d.backward((LL, (LH, HL, HH)))

        print("LH Contribution --> {}\n".format(np.sum(imgLH*imgLH)/np.sum(imgHH*imgHH)))

def getHHContribution(path, N):
    d = DWT()
    for i in range(N):

        LL, LH, HL, HH = HHtoBlack(path, N)
        imgHH_B = d.backward((LL, (LH, HL, HH)))

        LL, LH, HL, HH = HHtoBlack(path, N)
        imgHH = d.backward((LL, (LH, HL, HH)))

        print("HH Contribution --> {}\n".format(np.sum(imgHH_B*imgHH_B)/np.sum(imgHH*imgHH)))

def LLtoBlack(path, N):
    for i in range(N):

        LH, HL, HH = decomposition.readH(path, "{:03d}".format(i))
        LL = decomposition.readL(path, "{:03d}".format(i))

        y = math.ceil(LL.shape[0]/2)
        x = math.ceil(LL.shape[1]/2)

        LL[x][y][0] = 255
        LL[x][y][1] = 255
        LL[x][y][2] = 255

        return LL, LH, HL, HH

def LHtoBlack(path, N):
    for i in range(N):

        LH, HL, HH = decomposition.readH(path, "{:03d}".format(i))
        LL = decomposition.readL(path, "{:03d}".format(i))

        y = math.ceil(LH.shape[0]/2)
        x = math.ceil(LH.shape[1]/2)

        LH[x][y][0] = 255
        LH[x][y][1] = 255
        LH[x][y][2] = 255

        return LL, LH, HL, HH

def HLtoBlack(path, N):
    for i in range(N):

        LH, HL, HH = decomposition.readH(path, "{:03d}".format(i))
        LL = decomposition.readL(path, "{:03d}".format(i))

        y = math.ceil(HL.shape[0]/2)
        x = math.ceil(HL.shape[1]/2)

        HL[x][y][0] = 255
        HL[x][y][1] = 255
        HL[x][y][2] = 255

        return LL, LH, HL, HH

def HHtoBlack(path, N):
    for i in range(N):

        LH, HL, HH = decomposition.readH(path, "{:03d}".format(i))
        LL = decomposition.readL(path, "{:03d}".format(i))

        y = math.ceil(HH.shape[0]/2)
        x = math.ceil(HH.shape[1]/2)

        HH[x][y][0] = 255
        HH[x][y][1] = 255
        HH[x][y][2] = 255

        return LL, LH, HL, HH

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
                        help="Number of images/decompositions", default=1, type=int)

    args = parser.parse_args()
    path = os.path.dirname(args.decompositions)

    '''GET THE CONTRUBITON OF EACH SUBBAND'''
    getLLContribution(args.decompositions, args.N)
    getHLContribution(args.decompositions, args.N)
    getLHContribution(args.decompositions, args.N)
    getHHContribution(args.decompositions, args.N)