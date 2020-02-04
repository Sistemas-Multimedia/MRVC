#!/usr/bin/env python

import os
import argparse
try:
    import cv2
except:
    os.system("pip3 install opencv-python --user")
try:
    import numpy as np
except:
    os.system("pip3 install numpy -user")

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description = "Quantize an image\n\n"
                                 "Example:\n\n"
                                 "  python -O quantize.py -i ../sequences/stockholm/000.png -o /tmp/000.png -q 64\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--input", help="Input image", default="../sequences/stockholm/000.png")
parser.add_argument("-o", "--output", help="Output image", default="/tmp/000.png")
parser.add_argument("-q", "--q_step", type=int, help="Quantization step", default=32)

args = parser.parse_args()

image = cv2.imread(args.input, -1)

if __debug__:
    print("Quantizing with step {}".format(args.q_step))

tmp = image.astype(np.float32)
tmp -= 32768
#image = tmp.astype(np.int16)

#if __debug__:
#    print("Max value at input: {}".format(np.amax(image)))
#    print("Min value at input: {}".format(np.amin(image)))

#image //= args.q_step
#if __debug__:
#    print("Max value at input: {}".format(np.amax(image)))
#    print("Min value at input: {}".format(np.amin(image)))

#image *= args.q_step
#image += ((args.q_step//2)-1)

image = (tmp/args.q_step).astype(np.int16)*args.q_step

if __debug__:
    print("Max value at output: {}".format(np.amax(image)))
    print("Min value at output: {}".format(np.amin(image)))

tmp = image.astype(np.float32)
tmp += 32768
image = tmp.astype(np.uint16)

cv2.imwrite(args.output, image)

