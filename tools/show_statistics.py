import cv2
import numpy as np
import math

def compute_entropy(d, counter):
    for x in d:
        d[x] /= 1.*counter

    en = 0.
    for x in d:
        en += d[x] * math.log(d[x])/math.log(2.0)

    return -en


image = cv2.imread('/tmp/000_LL', -1)

width = image.shape[0]
height = image.shape[1]
number_of_pixels = width * height
components = image.shape[2]

histogram = [None]*components
for i in range(components):
    histogram[i] = {}

for y in range(height):
    for x in range(width):
        for c in range(components):
            val = image[y,x,c]
            if val not in histogram[c]:
                histogram[c] = 1
            else:
                histogram[c] += 1

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
