#!/usr/bin/env python3

# Note: swap the above line with the following two ones to switch
# between the standard and the optimized running mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

"""subbnad_gain.py: Calculates the gain using DWT and !DWT."""

import cv2
import numpy as np
import math
import argparse
import subprocess
# from cv2 import Sobel
# from skimage import data, draw, transform, util, color, filters
# import pylab

# Creates the command line arguments
parser = argparse.ArgumentParser("Calculates gain of an image calculating energies")
parser.add_argument("-i", help="Image to calculate gain without extension example: 000", default = "000")
parser.add_argument("-path", "--path", help="Dir where the files the I/O files are placed", default="/tmp/")                                
args = parser.parse_args() # Parses all the arguments

# Applies the DWT forward transform
subprocess.run("python3 -O ../src/DWT.py -i {} -p {}".format(args.i, args.path), shell=True, check=True)

image = cv2.imread((args.path+"HH000.png"), -1) 
print("Image shape: ", image.shape)
img_bandHH = image * 0
width = image.shape[0]
height = image.shape[1]

# Adds a pixel in the middle of the band
img_bandHH[width//2][height//2][0] = 65535
img_bandHH[width//2][height//2][1] = 65535
img_bandHH[width//2][height//2][2] = 65535
image_black = image * 0

# Black the images for every subband
subprocess.run("mkdir -p {}gainCalc".format(args.path), shell=True) # locates the images before calculating the base
cv2.imwrite("{}gainCalc/LL000.png".format(args.path), image_black.astype(np.uint16))
cv2.imwrite("{}gainCalc/HL000.png".format(args.path), image_black.astype(np.uint16))
cv2.imwrite("{}gainCalc/LH000.png".format(args.path), image_black.astype(np.uint16))
cv2.imwrite("{}gainCalc/HH000.png".format(args.path), img_bandHH.astype(np.uint16))
# !DWT to reconstruct to create the base
subprocess.run("python3 -O ../src/DWT.py -i {} -p {} -b".format(args.i, args.path+"gainCalc/"), shell=True, check=True)
subprocess.run("python3 -O ../src/DWT.py -i {} -p {} -b".format(args.i, args.path), shell=True, check=True)
# Reads the two images
base = cv2.imread((args.path+"gainCalc/"+"000.png"), -1) 
img_reconstructed = cv2.imread((args.path+"000.png"), -1)

def calc_energy(input_image):
    energy = np.power(input_image, 2)
    energy = np.sum(energy)
    print("Energy:  {}".format(energy))
    return energy

# Calculates the gain
gain = calc_energy(img_reconstructed)/ calc_energy(base)
print("Total gain:  {}".format(gain))

