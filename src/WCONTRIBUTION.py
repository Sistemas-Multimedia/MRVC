#!/usr/bin/env python

# Note: swap the above line with the following two ones to switch
# between the standar and the optimized mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

import sys
import os
sys.path.insert(0, "..")
from src.IO import decomposition

class WCONTRIBUTION:

    def __init__(self):

    def getContribution(s="/tmp/stockholm_"):

        LH, HL, HH = decomposition.read("{}{:03d}".format(s, 0))
        LL = decomposition.readL("{}{:03d}".format(s, 0))

        '''CALCULAR ENERGIA DE CADA BANDA'''
        print("JLL --> {}\n".format('Energia LL/Energia HH'))
        print("JHL --> {}\n".format('Energia HL/Energia HH'))
        print("JLH --> {}\n\n".format('Energia LH/Energia HH'))





if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
#        "  yes | cp -rf ../sequences/stockholm/ /tmp/\n"
    parser = argparse.ArgumentParser(
        description = "Wavelet Contribution Calculator\n\n"
        "Example:\n\n"
        "  python3 -O ./WCONTRIBUTION.py -d /tmp/stockholm_ -K 5 \n",
        formatter_class=CustomFormatter)

    parser.add_argument("-d", "--decompositions",
                        help="Sequence of decompositions", default="/tmp/stockholm_")

    parser.add_argument("-K",
                        help="Number of spatial levels", default=2, type=int)

    args = parser.parse_args()
    path = os.path.dirname(args.decompositions)

    '''Execute MDWT + MCDWT K times'''
    for i in range(args.K):

        print("#################################\n"
              "#########SPATIAL LEVEL {}#########\n"
              "#################################\n".format(i))

        d = WCONTRIBUTION()
        p = d.getContribution(args.decompositions)

        path += '/LL/'
        args.decompositions = path + os.path.basename(decompositions)