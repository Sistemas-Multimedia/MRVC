#!/usr/bin/env python

import cv2
import numpy as np
import math
import argparse
from cv2 import Sobel
from skimage import data, draw, transform, util, color, filters
import pylab



class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

parser = argparse.ArgumentParser(description = "Displays information about an image\n\n"
                                 "Example:\n\n"
                                 "  python show_statistics.py -i ../sequences/stockholm/000\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--image",
                    help="Input image", default="/tmp/stockholm/000")

args = parser.parse_args()

def compute_entropy(d, counter):
    for x in d:
        d[x] /= 1.*counter

    en = 0.
    for x in d:
        en += d[x] * math.log(d[x])/math.log(2.0)

    return -en

image = cv2.imread(args.image, -1)
component_depth = image.itemsize
#tmp = image.astype(np.float32)
#tmp -= 32768.0
#image = tmp.astype(np.int16)

width = image.shape[0]
height = image.shape[1]
number_of_pixels = width * height
components = image.shape[2]

def calc_energy(img):
    energy = np.power(img, 2)
    energy = np.sum(energy)
    return energy

energy = calc_energy(image)

histogram = [None]*components
for c in range(components):
    histogram[c] = {}

for y in range(width):
    for x in range(height):
        for c in range(components):
            val = image[y,x,c]
            if val not in histogram[c]:
                histogram[c][val] = 1
            else:
                histogram[c][val] += 1

entropy = [None]*components
for c in range(components):
    entropy[c] = compute_entropy(histogram[c], number_of_pixels)

max = [None] * components
min = [None] * components
dynamic_range = [None] * components
mean = [None] * components
for c in range(components):
    max[c] = np.amax(image[:,:,c])
    min[c] = np.amin(image[:,:,c])
    dynamic_range[c] = max[c] - min[c]
    mean[c] = np.mean(image[:,:,c])

print("Image: {}".format(args.image))
print("Width: {}".format(width))
print("Height: {}".format(height))
print("Components: {}".format(components))
print("Component depth: {}".format(component_depth))
print("Number of pixels: {}".format(number_of_pixels))
print("Energy: {}".format(energy))
for c in range(components):
    print("Max value of component {}: {}".format(c, max[c]))
for c in range(components):
    print("Min value of component {}: {}".format(c, min[c]))
for c in range(components):
    print("Dynamic range of component {}: {}".format(c, dynamic_range[c]))
for c in range(components):
    print("Mean of component {}: {}".format(c, mean[c]))
for c in range(components):
    print("Entropy of component {}: {}".format(c, entropy[c]))
