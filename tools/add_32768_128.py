#!/usr/bin/env python

import cv2
import numpy as np
import sys

input = sys.argv[1]
output = sys.argv[2]
image = cv2.imread(input, -1).astype(np.uint16)
print(np.amax(image), np.amin(image))
image += (32768-128)
print(np.amax(image), np.amin(image))
cv2.imwrite(output, image.astype(np.uint16))
