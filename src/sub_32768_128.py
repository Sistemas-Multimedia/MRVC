#!/usr/bin/env python

import cv2
import numpy as np
import sys

input = sys.argv[1]
output = sys.argv[2]
image = cv2.imread(input, -1)

if __debug__:
    print("Max value at input: {}".format(np.amax(image)))
    print("Min value at input: {}".format(np.amin(image)))

image = np.clip(image, 32768-128, 32768-128+255)
image -= (32768-128)

if __debug__:
    print("Substracting {}".format(32768-128))

if __debug__:
    print("Max value at output: {}".format(np.amax(image)))
    print("Min value at output: {}".format(np.amin(image)))

cv2.imwrite(output, image.astype(np.uint8))