#!/usr/bin/env python

import os
import sys
import argparse
try:
    import cv2
except:
    os.system("pip3 install opencv-python --user")
try:
    import numpy as np
except:
    os.system("pip3 install numpy --user")

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description = "Substracts (and clips to [0,255]) an offset to an image\n"
                                 "and converts it from 16 bits/component to 8 bits/component.\n"
                                 "Both, the input and the output are unsigned integers.\n\n"
                                 "Example:\n\n"
                                 "  substract_offset -i ../sequences/stockholm/000.png -o /tmp/000.png -f 32768\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--input", help="Input image", default="../sequences/stockholm/000.png")
parser.add_argument("-o", "--output", help="Input image", default="/tmp/000.png")
parser.add_argument("-f", "--offset", type=int, help="Offset", default=32768)

args = parser.parse_args()

image = cv2.imread(args.input, -1)

if __debug__:
    print("Image depth: {}".format(image.dtype))
    print("Max value at input: {}".format(np.amax(image)))
    print("Min value at input: {}".format(np.amin(image)))

image = np.clip(image, args.offset, args.offset+255)
image = image.astype(np.float32)
image -= args.offset
image = image.astype(np.uint8)

if __debug__:
    print("Substracting {}".format(args.offset))
    print("Max value at output: {}".format(np.amax(image)))
    print("Min value at output: {}".format(np.amin(image)))

cv2.imwrite(args.output, image.astype(np.uint8))
