#!/usr/bin/env python3

# Note: swap the above line with the following two ones to switch
# between the standard and the optimized running mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

"""quantizer.py: Scalar Image quantizer for normal images in png, DO NOT USE WITH 16 BITS IMAGES."""

import cv2
import numpy as np
import math
import argparse
import subprocess
from cv2 import Sobel
from skimage import data, draw, transform, util, color, filters
import pylab
from PIL import Image

# Creates the command line arguments
parser = argparse.ArgumentParser("Calculates gain of an image calculating energies\nMore info: from https://rosettacode.org/wiki/Color_quantization#Python")
parser.add_argument("-i", help="Input image: /tmp/HH000.png", default = "/tmp/HH000.png")
parser.add_argument("-o", help="Output image: /tmp/quantized.png", default = "/tmp/quantized.png")
parser.add_argument("-step", "--step", help="Quantization steps", default = 8, type = int)                                
args = parser.parse_args() # Parses all the arguments
K = args.step
img = cv2.imread(args.i, -1)

# Light quantizer not using any improvement
imgTest = Image.open(args.i)
im2Test = imgTest.quantize(K)
im2Test.show()

#cv2.imshow('Quantized Image K = {}'.format(K),im2Test)
cv2.imshow('Original Image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
im2Test.save("/tmp/Quantized_normal_{}.png".format(K),"PNG")
