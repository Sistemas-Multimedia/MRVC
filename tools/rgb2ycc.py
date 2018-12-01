#!/usr/bin/env python

import cv2
import argparse

# Parse arguments
parser = argparse.ArgumentParser(description='This script converts a RGB image to YCbCr.')
parser.add_argument('-i','--input', help='Input file name',required=True)
parser.add_argument('-o','--output',help='Output file name', required=True)
args = parser.parse_args()

# Read image
image_rgb = cv2.imread(args.input, -1)
if image_rgb is None:
    raise Exception('{} not found'.format(args.input))

# Convert to YCbCr
image_ycc = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2YCR_CB)

# Write image
cv2.imwrite(args.output, image_ycc)
