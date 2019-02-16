#!/usr/bin/env python

import cv2
import numpy as np
import sys
import argparse

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description = "Substracts (and clips to [0,255]) an offset to an image\n\n"
                                 "Example:\n\n"
                                 "  substract_offset -i ../sequences/stockholm/000 -o /tmp/000 -f 32640\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--input",
                    help="Input image", default="../sequences/stockholm/000.png")

parser.add_argument("-o", "--output",
                    help="Input image", default="/tmp/000.png")

args = parser.parse_args()

image = cv2.imread(args.input, -1).astype(np.uint16)

if __debug__:
    print("Max value at input: {}".format(np.amax(image)))
    print("Min value at input: {}".format(np.amin(image)))

image = np.clip(image, 0, 255).astpye(np.uint8)
#image -= args.offset

if __debug__:
    print("Converting to 8bpp")

if __debug__:
    print("Max value at output: {}".format(np.amax(image)))
    print("Min value at output: {}".format(np.amin(image)))

cv2.imwrite(args.output, image)
