#!/usr/bin/env python3

# Generates the RD points of MCDWT.

import sys
sys.path.insert(0, "..")
import os
import argparse
from tools.quantize import quantize
from src.DWT import DWT
try:
    import cv2
except:
    os.system("pip3 install opencv-python --user")
try:
    import numpy as np
except:
    os.system("pip3 install numpy --user")
try:
    import skimage.metrics
except:
    os.system("pip3 install scikit-image --user")

if __debug__:
    import time
    def normalize(x):
        return ((x - np.amin(x)) / (np.amax(x) - np.amin(x)))

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description = "Generates the RD points of a MCDWT code-stream\n\n"
                                 "Example:\n\n"
                                 "  python3 -O RD_curve.py -p /tmp/\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-p", "--prefix", help="Dir where the files the I/O files are placed", default="/tmp/")
parser.add_argument("-N", "--decompositions", help="Number of input decompositions", default=5, type=int)
parser.add_argument("-T", "--iterations", help="Number of temporal iterations", default=2, type=int)

args = parser.parse_args()
dwt = DWT()

def process_subband(subband, q_step):
    original_sb = cv2.imread(args.prefix + subband + "000.png", -1)
    original_sb = original_sb.astype(np.float32)
    original_sb -= 32768
    quantized_sb = quantize(original_sb, q_step)
    zero = np.zeros((original_sb.shape[0], original_sb.shape[1], 3))
    reconstruction = dwt.backward([quantized_sb, [zero, zero, zero]])
    if __debug__:
        cv2.imshow("reconstruction", normalize(reconstruction))
        while cv2.waitKey(1) & 0xFF != ord('q'):
            time.sleep(0.1)
    _1 = reconstruction + 32768
    _1 = reconstruction.astype(np.uint16)
    cv2.imwrite("/tmp/1.png", _1)
    original = cv2.imread(args.prefix + "000.png", -1)
    original = original.astype(np.float32)
    original -= 32768
    MSE = skimage.metrics.mean_squared_error(original, reconstruction)
    rate = os.path.getsize("/tmp/1.png")
    return (subband, MSE, rate)

DR_points = []

# GOP 0
for q_step in [(1 << i) for i in range(9,-1,-1)]:
    DR_points.append(process_subband("LL", q_step))
    DR_points.append(process_subband("LH", q_step))

print(DR_points)

