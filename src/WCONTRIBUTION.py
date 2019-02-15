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

    parser.add_argument("-N",
                        help="Number of images/decompositions", default=5, type=int)

    args = parser.parse_args()
    path = os.path.dirname(args.decompositions)

    '''PRIMERA TRANSFORMACIÓN DIRECTA'''
    d = MDWT()
    d.forward('../sequences/stockholm/', args.decompositions, args.N)

    '''MODIFICAMOS LA SUBBANDA HH PONIENDOLA EN NEGRO CON UN PUNTO BLANCO EN EL CENTRO'''
    for i in range(args.N):

        LH, HL, HH = decomposition.readH("{}{:03d}".format(args.decompositions, i))
        LL = decomposition.readL("{}{:03d}".format(args.decompositions, i))

        y = math.ceil(HH.shape[0]/2)
        x = math.ceil(HH.shape[1]/2)

        HH = HH * 0
        HH[x][y][0] = 255
        HH[x][y][1] = 255
        HH[x][y][2] = 255

        decomposition.writeH([LH,HL,HH],"{}{:03d}".format(args.decompositions, i))

   

    '''RECONSTRUIMOS LA IMAGEN Y VOLVEMOS A DESCOMPONERLA PARA CALCULAR LA GANANCIA'''
    d.backward(args.decompositions, '/tmp/recons_MDWT_', args.N)
    d.forward('/tmp/recons_MDWT_', args.decompositions, args.N)

    '''OBTENEMOS LA GANANCIA DE CADA SUBBANDA'''
    for i in range(args.N):

        LH, HL, HH = decomposition.readH("{}{:03d}".format(args.decompositions, i))
        LL = decomposition.readL("{}{:03d}".format(args.decompositions, i))


        '''CALCULAR GANANCIA DE CADA SUBBANDA'''
        print("JLL --> {}\n".format(np.sum(LL*LL)/np.sum(HH*HH)))
        print("JHL --> {}\n".format(np.sum(HL*HL)/np.sum(HH*HH)))
        print("JLH --> {}\n\n".format(np.sum(LH*LH)/np.sum(HH*HH)))