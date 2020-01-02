#!/usr/bin/env python

# Note: swap the above line with the following two ones to switch
# between the standard and the optimized running mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

import numpy as np
import pywt
import math
import sys

sys.path.insert(0, "..")
from src.IO import image
from src.IO import decomposition

class DWT:

    def forward(self, image):
        '''Forward 1-iteration 2D-DWT of a color image.

        Input:
        -----

            an image: an array[y, x, component] with a color (usually YUV) image.

                  x
             +---------------+
             |              Y|-+ component
           y |               |U|-+
             |               | |V|
             |     image     | | |
             |               | | |
             |               | | |
             |               | | |
             +---------------+ | |
               +---------------+ |
                 +---------------+


        Output:
        ------

            a decomposition: a tuple (L, H), where L (the low-frequencie
            subband) is an array[y, x, component], and H (high-frequencies
            subbands) is a tuple (LH, HL, HH), where LH, HL, HH are
            array[y, x, component], with the color decomposition.

                 x
             +-------+-------+
             |       |      Y|-+ component
           y |  LL   |  HL   |U|-+
             |       |       | |U|
             +-------+-------+ | |
             |       |       |-+ |
             |  LH   |  HH   | |-+
             |       |       | | |
             +-------+-------+ | |
               +-------+-------+ |
                 +-------+-------+

            This structure provides 2 spatial resolution levels: LL and
            image.

        '''

        y = math.ceil(image.shape[0]/2)
        x = math.ceil(image.shape[1]/2)
        LL = np.ndarray((y, x, 3), np.float64)
        LH = np.ndarray((y, x, 3), np.float64)
        HL = np.ndarray((y, x, 3), np.float64)
        HH = np.ndarray((y, x, 3), np.float64)
        if __debug__:
            print("image: max={} min={}".format(np.amax(image), np.amin(image)))
        for c in range(3):
            LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c]) = pywt.dwt2(image[:,:,c], 'bior3.5', mode='per')
        if __debug__:
            print("DWT::forward: LL: max={} min={}".format(np.amax(LL), np.amin(LL)))
            print("DWT::forward: LH: max={} min={}".format(np.amax(LH), np.amin(LH)))
            print("DWT::forward: HL: max={} min={}".format(np.amax(HL), np.amin(HL)))
            print("DWT::forward: HH: max={} min={}".format(np.amax(HH), np.amin(HH)))

        decomposition = LL, (LH, HL, HH)
        return decomposition

    def backward(self, decomposition):
        '''2D 1-iteration inverse DWT of a color decomposition.

        Input:
        -----

            decomposition: the input decomposition (see forward transform).

        Output:
        ------

            an image: the inversely transformed image (see forward transform).

        '''
        LL = decomposition[0]
        LH = decomposition[1][0]
        HL = decomposition[1][1]
        HH = decomposition[1][2]
        image = np.ndarray((LL.shape[0]*2, LL.shape[1]*2, 3), np.float64)
        for c in range(3):
            image[:,:,c] = pywt.idwt2((LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), 'bior3.5', mode='per')
        return image

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
    parser = argparse.ArgumentParser(
        description = "2D Discrete Wavelet (color) Transform\n\n"
        "Examples:\n\n"
        "  cp ../sequences/stockholm/000.png /tmp/\n"
        "  python3 -O DWT.py    -p /tmp/ -i 000 # Forward transform\n"
        "  python3 -O DWT.py -b -d /tmp/ -i 000 # Backward transform\n",
        formatter_class=CustomFormatter)

    parser.add_argument("-b", "--backward", action='store_true', help="Performs backward transform")
    parser.add_argument("-p", "--prefix", help="Dir where the files the I/O files are placed", default="/tmp/")
    parser.add_argument("-i", "--index", help="Index of the image/decomposition", default="000")

    args = parser.parse_args()

    dwt = DWT()
    if args.backward:
        if __debug__:
            print("Backward transform")
        d = decomposition.read(args.prefix, args.index)
        i = dwt.backward(d)
        image.write(i, args.prefix, args.index)
    else:
        if __debug__:
            print("Forward transform")
        i = image.read(args.prefix, args.index)
        d = dwt.forward(i)
        decomposition.write(d, args.prefix, args.index)
