#!/usr/bin/env python

import cv2
import numpy as np
import math
import argparse

columns_format = 60
def myprint(str):
        print(str.ljust(columns_format))
    
class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

parser = argparse.ArgumentParser(description = "Displays information about an image\n\n"
                                 "Example:\n\n"
                                 "  python show_statistics.py -i ../sequences/stockholm/000.png\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--image", help="Input image", default="/tmp/stockholm/000.png")
parser.add_argument("-o", "--offset", type=int, help="Offset used for representing the true values", default=32768)
#parser.add_argument("-r", "--range", type=int, help="Range of max and min shown values", default=5)

args = parser.parse_args()

myprint("Filename = {}".format(args.image))
myprint("Offset = {}".format(args.offset))

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

myprint("Image: {}".format(args.image))
myprint("Width: {}".format(width))
myprint("Height: {}".format(height))
myprint("Components: {}".format(components))
myprint("Component depth: {}".format(component_depth))
myprint("Number of pixels: {}".format(number_of_pixels))
for c in range(components):
    myprint("Max value of component {}: {} ({})".format(c, max[c], max[c]-args.offset))
for c in range(components):
    myprint("Min value of component {}: {} ({})".format(c, min[c], min[c]-args.offset))
for c in range(components):
    myprint("Dynamic range of component {}: {}".format(c, dynamic_range[c]))
for c in range(components):
    myprint("Mean of component {}: {} ({})".format(c, mean[c], mean[c]-args.offset))
for c in range(components):
    myprint("Entropy of component {}: {}".format(c, entropy[c]))

indices = [None] * components
for c in range(components):
    myprint("Component {}".format(c))
    myprint("{0: <8} {1: <10} {2: <10}".format("position", "coordinates", "value"))
    # https://stackoverflow.com/questions/30577375/have-numpy-argsort-return-an-array-of-2d-indices
    indices[c] = np.dstack(np.unravel_index(np.argsort(abs(image[:,:,c]).ravel()), (width, height)))
    #myprint(indices[c].shape)
    counter = 1
    while counter <= 10:
        coordinates = indices[c][0][counter]
        val = image[indices[c][0][indices[c].shape[1]-counter][0], indices[c][0][indices[c].shape[1]-counter][1], c]
        myprint("{:8d}   {} {} ({})".format(counter, coordinates, val, val-args.offset))
        counter += 1
    counter = number_of_pixels - 1 - 10
    while counter <= number_of_pixels - 1:
        coordinates = indices[c][0][counter]
        val = image[indices[c][0][indices[c].shape[1]-counter][0], indices[c][0][indices[c].shape[1]-counter][1], c]
        myprint("{:8d}   {} {} ({})".format(counter, coordinates, val, val-args.offset))
        counter += 1

