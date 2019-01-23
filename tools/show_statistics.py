import cv2
import numpy as np
import math
import argparse

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

width = image.shape[0]
height = image.shape[1]
number_of_pixels = width * height
components = image.shape[2]

histogram = [None]*components
for i in range(components):
    histogram[i] = {}

for y in range(width):
    for x in range(height):
        for c in range(components):
            val = image[y][x][c]
            if val not in histogram[c]:
                histogram[c][val] = 1
            else:
                histogram[c][val] += 1

entropy = [None]*components
for c in range(components):
    entropy[c] = compute_entropy(histogram[c], number_of_pixels)
    
max = np.amax(image)
min = np.amin(image)
dynamic_range = max - min

print("Width: {}".format(width))
print("Height: {}".format(height))
print("Components: {}".format(components))
print("Number of pixels: {}".format(number_of_pixels))
print("Max value: {}".format(max))
print("Min value: {}".format(min))
print("Dynamic range: {}".format(dynamic_range))
for c in range(components):
    print("Entropy of component {}: {}".format(c, entropy[c]))
