#!/usr/bin/env python

import os

try:
    import cv2
except:
    os.system("pip3 install opencv-python --user")
try:
    import numpy as np
except:
    os.system("pip3 install numpy --user")

import argparse

try:
    import skimage.metrics
except:
    os.system("install scikit-image --user")

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description = "Compute the Mean Square Error (MSE) betweem two images\n\n"
                                 "Example:\n\n"
                                 "  python3 -O MSE.py -i ../sequences/stockholm/000.png -j /tmp/000.png\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-x", help="Input image 1", default="../sequences/stockholm/000.png")
parser.add_argument("-y", help="Input image 2", default="/tmp/000.png")

args = parser.parse_args()

x = cv2.imread(args.x, -1)
y = cv2.imread(args.y, -1)

MSE = skimage.metrics.mean_squared_error(x, y)

print("{}".format(MSE))
