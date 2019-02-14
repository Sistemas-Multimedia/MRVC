#!/usr/bin/env python

import cv2
import numpy as np
import sys
import argparse
from subprocess import check_call
from subprocess import CalledProcessError

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description = "Adds an offset to an image\n\n"
                                 "Example:\n\n"
                                 "  add_offset -i ../sequences/stockholm/000 -o /tmp/000 -f 32640\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--input",
                    help="Input image", default="../sequences/stockholm/000")

parser.add_argument("-o", "--output",
                    help="Input image", default="/tmp/000")

parser.add_argument("-f", "--offset", type=int,
                    help="Offset", default=32768-128)

args = parser.parse_args()

input = args.input
output = args.output
offset = args.offset
image = cv2.imread(input, -1).astype(np.uint16)

if __debug__:
    print("Max value at input: {}".format(np.amax(image)))
    print("Min value at input: {}".format(np.amin(image)))

if __debug__:
    print("Adding {}".format(offset))

image += offset

if __debug__:
    print("Max value at output: {}".format(np.amax(image)))
    print("Min value at output: {}".format(np.amin(image)))

cv2.imwrite(output + ".png", image.astype(np.uint16))
try:
    check_call("mv " + output + ".png " + output, shell=True)
except CalledProcessError:
    print("Exception {}".format(traceback.format_exc()))

