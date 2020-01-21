#!/usr/bin/env python3

import cv2
import numpy as np
#import sys
import argparse
#from subprocess import check_call
#from subprocess import CalledProcessError

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description = "Adds an offset to an image and coverts it from\n"
                                 "8 bpp/component to 16 bpp/component. The pixels of the input\n"
                                 "and the output image are represented as integer without sign.\n\n"
                                 "Example:\n\n"
                                 "  python3 add_offset -i ../sequences/stockholm/000.png -o /tmp/000.png -f 32768\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--input", help="Input image", default="../sequences/stockholm/000.png")
parser.add_argument("-o", "--output", help="Input image", default="/tmp/000.png")
parser.add_argument("-f", "--offset", type=int, help="Offset", default=32768)

args = parser.parse_args()

image = cv2.imread(args.input, -1).astype(np.uint16)

if __debug__:
    print("Max value at input: {}".format(np.amax(image)))
    print("Min value at input: {}".format(np.amin(image)))

if __debug__:
    print("Adding {}".format(args.offset))

image += args.offset

if __debug__:
    print("Max value at output: {}".format(np.amax(image)))
    print("Min value at output: {}".format(np.amin(image)))

cv2.imwrite(args.output, image)
#try:
#    check_call("mv " + output + ".png " + output, shell=True)
#except CalledProcessError:
#    print("Exception {}".format(traceback.format_exc()))

