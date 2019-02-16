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
                                 "  python -O quantize.py -i ../sequences/stockholm/000.png -o /tmp/000.png -q 64\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--input",
                    help="Input image", default="../sequences/stockholm/000.png")

parser.add_argument("-o", "--output",
                    help="Input image", default="/tmp/000.png")

parser.add_argument("-q", "--q_step", type=int,
                    help="Quantization step", default=32)

args = parser.parse_args()

image = cv2.imread(args.input, -1)

if __debug__:
    print("Max value at input: {}".format(np.amax(image)))
    print("Min value at input: {}".format(np.amin(image)))

if __debug__:
    print("Quantizing with step {}".format(args.q_step))

tmp = image.astype(np.float32)
tmp -= 32768
image = tmp.astype(np.int16)
image //= args.q_step
image *= args.q_step
image += (args.q_step//2)
tmp = image.astype(np.float32)
tmp += 32768
image = tmp.astype(np.uint16)

if __debug__:
    print("Max value at output: {}".format(np.amax(image)))
    print("Min value at output: {}".format(np.amin(image)))

cv2.imwrite(args.output, image)

