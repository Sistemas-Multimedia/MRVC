#!/usr/bin/env python

import numpy as np
import sys

from DWT import DWT
sys.path.insert(0, "..")
from src.IO import decomposition

class MCDWT:

    def forward(self, prefix = "/tmp/", N=5, T=2; K=2):
        _2d_transform = MDWT()
        for k in range(K):
            _2d_transform.forward(prefix, N)
            tmp = decomposition.readL(prefix, "000")
            t_transform = MCDWT(tmp.shape) # t_transform = SMCTF(tmp.shape)
            t_transform.forward(prefix + _2d_level, N, T)
            _2d_level += "LL"

    def backward(self, prefix = "/tmp/", N=5, T=2, K=2):
        _2d_transform = MDWT()
        _2d_level = "LL"*K
        for k in range(K):
            tmp = decomposition.readL(prefix, "000")
            t_transform = MCDWT(tmp.shape) # t_transform = SMCTF(tmp.shape)
            t_transform.backward(prefix + _2d_level, N, T)
            _2d_transform.backward(prefix, N)
            _2d_level = "LL"*k

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
    parser.add_argument("-K", help="Number of spatial levels", default=2, type=int)
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
