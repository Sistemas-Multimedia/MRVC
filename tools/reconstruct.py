
#!/usr/bin/env python3

# Note: swap the above line with the following two ones to switch
# between the standard and the optimized running mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''


import numpy as np
import pywt
import math
import sys
import subprocess
import argparse
import cv2
import numpy

# Creates the command line arguments 
parser = argparse.ArgumentParser("This reconstructs the image from 16 bits back to normal")
parser.add_argument("-i", help="input image to reconstruct", )
parser.add_argument("-o", help="output image" ,default="output.png")

# Pareses all the arguments
args = parser.parse_args()

# Asign input and output 
if args.i != None:
    input = args.i
else:
    print("Input file missing, try:  reconstruct.py -i image16bits.png ")
    exit()

if args.o != None:
    output = args.o



image = cv2.imread(input, -1)


image = np.clip(image, 32768-128, 32768-128+255)
image -= (32768-128)

cv2.imwrite(output, image.astype(np.uint8))