#!/usr/bin/env python

# Note: swap the above line with the following two ones to switch
# between the standard and the optimized running mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

import numpy as np
import pywt
import math
import sys
import os

sys.path.insert(0, "..")
from src.IO import image
from src.IO import decomposition

class DWT:

    def forward(self, image):
        '''Forward 1-iteration 2D-DWT of a color image.

        Input:
        -----

            image: an array[y, x, component] with a color image.

                  x
             +---------------+
             |              Y|-+ component
           y |               |U|-+
             |               | |V|
             |             or| | |
             |               |r| |
             |               | |r|
             |              R| | |
             +---------------+G| |
               +---------------+B|
                 +---------------+


        Output:
        ------

            a decomposition: a tuple (L, H), where L (low-frequencies subband)
            is an array[y, x, component], and H (high-frequencies
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
             |       |      R| | |
             +-------+-------+G| |
               +-------+-------+B|
                 +-------+-------+

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
            LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c]) = pywt.dwt2(image[:,:,c], 'db5', mode='per')
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
            image[:,:,c] = pywt.idwt2((LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), 'db5', mode='per')
        return image

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
    parser = argparse.ArgumentParser(
        description = "2D Discrete Wavelet (color) Transform\n\n"
        "Examples:\n\n"
        "  rm -rf /tmp/stockholm/\n"
        "  mkdir /tmp/stockholm\n"
        "  cp ../sequences/stockholm/000.png /tmp/\n"
        "  ./DWT.py    -i /tmp/000 -d /tmp/000/ # Forward transform\n"
        "  rm /tmp/stockholm/000                                   # Not really necessary\n"
        "  ./DWT.py -b -d /tmp/stockholm_000 -i /tmp/stockholm/000 # Backward transform\n",
        formatter_class=CustomFormatter)

    parser.add_argument("-b", "--backward", action='store_true',
                        help="Performs backward transform")

    parser.add_argument("-p", "--prefix", help="Prefix", default="/tmp/")
    parser.add_argument("-s", "--suffix", help="Suffix", default="000.png")
    
    
    parser.add_argument("-i", "--image",
                        help="File with the image", default="000")

    parser.add_argument("-d", "--decomposition",
                        help="Directory where the files LL, LH, HL, and HH are localized", default="000")

    args = parser.parse_args()

    dwt = DWT()
    if args.backward:
        if __debug__:
            print("Backward transform")
        d = decomposition.read(args.prefix, args.suffix)
        i = dwt.backward(d)
        image.write(i, args.prefix, args.suffix)
    else:
        if __debug__:
            print("Forward transform")
        i = image.read(args.prefix, args.suffix)
        d = dwt.forward(i)
        decomposition.write(d, args.prefix, args.suffix)
