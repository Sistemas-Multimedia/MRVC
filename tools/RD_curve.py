#!/usr/bin/env python3

# Generates the RD points of MCDWT.
#
# Algorithm:
#
# 1. Create a zero structure z with MCDWT.
# 2. Create a real video structure v with MCDWT.
# 3. For each subband s in v:
# 3.1. For each quantization step q in {1, 2, ..., infinite}:
# 3.1.1. Copy s to z.
# 3.1.2. Quantize s using q.
# 3.1.3. Reconstruct the video v'.
# 3.1.4. Compute the distortion between v and v'.
#
# Note: the last quantization step should be "infinite" in order to
# restore the original zero subband in z for the next iteration of
# loop of Step 3.

import glob
import sys
sys.path.insert(0, "..")
import os
import argparse
from tools.quantize import quantize
from src.DWT import DWT
from src.IO.decomposition import read as read_decomposition
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

N = 5
iters = 2

parser.add_argument("-w", "--width", help="Widht of the video", default="1280")
parser.add_argument("-e", "--height", help="Height of the video", default="768")
parser.add_argument("-p", "--prefix", help="Dir where the files the I/O files are placed", default="/tmp/")
parser.add_argument("-N", "--decompositions", help="Number of input decompositions", default=N, type=int)
parser.add_argument("-T", "--iterations", help="Number of temporal iterations", default=iters, type=int)

args = parser.parse_args()

# 1. Create the black original sequence.
os.system("rm -rf /tmp/zero")
os.system("mkdir /tmp/zero")
for i in range(N):
    ii = "{:03d}".format(i)
    os.system("bash ./create_black_image.sh -o /tmp/zero/" + str(ii) + ".png" +
              " -w " + str(args.width) + " -h " + str(args.height))
os.system("python3 ../src/MCDWT.py" + " -p /tmp/zero" + " -N " +
          str(args.decompositions) + " -T " + str(args.iterations))

# 2. Create the video structure.
os.system("python3 ../src/MCDWT.py" + " -p " + args.prefix + " -N " +
          str(args.decompositions) + " -T " + str(args.iterations))

# 3. For each subband in v:
for s in os.listdir("/tmp/zero/"):

dwt = DWT()
              
def process_subband2(subband, q_step):
    original_sb = cv2.imread(args.prefix + subband + "000.png", -1)
    original_sb = original_sb.astype(np.float32)
    original_sb -= 32768
    quantized_sb = quantize(original_sb, q_step)
    _1 = quantized_sb + 32768
    _1 = _1.astype(np.uint16)
    cv2.imwrite("/tmp/1.png", _1)
    rate = os.path.getsize("/tmp/1.png")
    zero = np.zeros((original_sb.shape[0], original_sb.shape[1], 3))
    if subband == 'LL':
        reconstruction = dwt.backward([quantized_sb, [zero, zero, zero]])
    elif subband == 'LH':
        reconstruction = dwt.backward([zero, [quantized_sb, zero, zero]])
    elif subband == 'HL':
        reconstruction = dwt.backward([zero, [zero, quantized_sb, zero]])
    else:
        reconstruction = dwt.backward([zero, [zero, zero, quantized_sb]])
        if __debug__:
            cv2.imshow("reconstruction", normalize(reconstruction))
            while cv2.waitKey(1) & 0xFF != ord('q'):
                time.sleep(0.1)
    original = cv2.imread(args.prefix + "000.png", -1)
    original = original.astype(np.float32)
    original -= 32768
    MSE = skimage.metrics.mean_squared_error(original, reconstruction)
    return (subband, MSE, rate)

def process_subband(subband, q_step):
    original_decomposition = read_decomposition(args.prefix, "000")
    if subband == 'LL':
        original_decomposition[0][:,:] = quantize(original_decomposition[0], q_step)
        _1 = original_decomposition[0] + 32768
        _1 = _1.astype(np.uint16)
        cv2.imwrite("/tmp/1.png", _1)
    elif subband == 'LH':
        original_decomposition[1][0][:,:] = quantize(original_decomposition[1][0], q_step)
        _1 = original_decomposition[1][0] + 32768
        _1 = _1.astype(np.uint16)
        cv2.imwrite("/tmp/1.png", _1)
    elif subband == 'HL':
        original_decomposition[1][1][:,:] = quantize(original_decomposition[1][1], q_step)
        _1 = original_decomposition[1][1] + 32768
        _1 = _1.astype(np.uint16)
        cv2.imwrite("/tmp/1.png", _1)
    else:
        original_decomposition[1][2][:,:] = quantize(original_decomposition[1][2], q_step)
        _1 = original_decomposition[1][2] + 32768
        _1 = _1.astype(np.uint16)
        cv2.imwrite("/tmp/1.png", _1)
    rate = os.path.getsize("/tmp/1.png")
    reconstruction = dwt.backward(original_decomposition)
    if __debug__:
        cv2.imshow("reconstruction", normalize(reconstruction))
        while cv2.waitKey(1) & 0xFF != ord('q'):
            time.sleep(0.1)
    original = cv2.imread(args.prefix + "000.png", -1)
    original = original.astype(np.float32)
    original -= 32768
    MSE = skimage.metrics.mean_squared_error(original, reconstruction)
    return (subband, MSE, rate)

DR_points = []

# GOP 0
for q_step in [(1 << i) for i in range(9,-1,-1)]:
    DR_points.append(process_subband("LL", q_step))
    DR_points.append(process_subband("LH", q_step))
    DR_points.append(process_subband("HL", q_step))
    DR_points.append(process_subband("HH", q_step))
    DR_points.append("\n")
    
    for i in DR_points:
        print(i, end='')
        #print(DR_points)
              
              
