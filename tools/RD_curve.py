#!/usr/bin/env python3

# Generates the RD points of MCDWT.
#
# Algorithm 1:
#
# 1. Create a zero structure z with MCDWT.
# 2. Create a video structure v with MCDWT.
# 3. For each subband s in v:
# 3.1. For each quantization step q in {2^0, 2^1, ..., 2^16}:
# 3.1.1. Copy s to z.
# 3.1.2. Quantize s (in z) using q.
# 3.1.3. Compute the length of quantized subband s.
# 3.1.4. Reconstruct the video from z.
# 3.1.5. Compute the distortion between the original video and the reconstruction.
# 3.1.6. Quantize by infinite all subbands of z.
#
# Note: the last quantization step should be "infinite" in order to
# restore the original zero subband in z for the next iteration of
# loop of Step 3.
#
# Algorithm 2:
#
# 1. Create a video structure v with MCDWT.
# 2. Do a copy of v as w.
# 3. For each subband s in v:
# 3.1. For each quantization step q in {2^16, 2^15, ..., 2^0}:
# 3.1.1. Copy v to w.
# 3.1.2. Quantize s (in w) using q.
# 3.1.3. Compute the length of the quantized subband s.
# 3.1.4. Reconstruct the video from w.
# 3.1.5. Compute the distortion between the original video and the reconstruction.
#
# Note: the last quantization step should be "1" in order to restore
# the original subband in w' for the next iteration of the Step 3.
#
# Y the progression determined by both algorithms is the same, MCDWT
# is biorthogonal.

import pandas as pd
import sys
sys.path.insert(0, "..")
import os
#from os import listdir
#from os.path import isfile, join
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
originals = "../sequences/stockholm/"

parser.add_argument("-w", "--width", help="Widht of the video", default="1280")
parser.add_argument("-e", "--height", help="Height of the video", default="768")
parser.add_argument("-p", "--prefix", help="Dir where the files the I/O files are placed", default="/tmp/")
parser.add_argument("-N", "--decompositions", help="Number of input decompositions", default=N, type=int)
parser.add_argument("-T", "--iterations", help="Number of temporal iterations", default=iters, type=int)
parser.add_argument("-O", "--originals", help="Original images", default=originals)

args = parser.parse_args()

def run(command):
    if __debug__:
        print(command)
    return os.popen(command).read()

# 1. Create the black original sequence.
run("rm -rf /tmp/zero/")
run("mkdir /tmp/zero/")
if __debug__:
    print("Number of decompositions = {}".format(args.decompositions))
    print("Number of iterations = {}".format(args.iterations))
for i in range(args.decompositions):
    ii = "{:03d}".format(i)
    run("bash ./create_black_image.sh -o /tmp/zero/" + str(ii) + ".png" + \
        " -w " + str(args.width) + " -h " + str(args.height))
run("python3 -O ../src/MDWT.py" + " -p /tmp/zero/" + " -N " + str(args.decompositions))
run("python3 -O ../src/MCDWT.py" + " -p /tmp/zero/" + " -N " + str(args.decompositions) + " -T " + str(args.iterations))
run("rm /tmp/zero/???.png") # Delete the images (keep the subbands)

# 2. Create the video structure.
run("cp " + args.originals + "*.png " + args.prefix)
run("python3 -O ../src/MDWT.py" + " -p " + args.prefix + " -N " + str(args.decompositions))
run("python3 -O ../src/MCDWT.py" + " -p " + args.prefix + " -N " + str(args.decompositions) + " -T " + str(args.iterations))

def save_RD(RD):
    print("#", end=' ')
    for subband in RD:
        print(subband, end='\t')
    print()
    print("subbands", RD.keys())
    print("points", RD.values())
    print("number of points for the first subband", len(list(RD.values())[0]))
    for p in range(len(list(RD.values()))):
        for s in range(len(list(RD.keys()))):
            print(RD[list(RD.keys())[s]][p])
        print('\t')
    #    for i in range(len(list(RD.values())[s])):
    #        for j in list(RD.values())[0]:
    #            print(j, sep='\t')
        #print(list(RD.values())[s])
    #    print()
#        for item in list(RD.keys())[i]:
#            print(item)
            #print("{}\t{}\t{}".format(item[0], item[1], item[2]), sep='\t', end='\t')
#    subband = RD.keys()[0]
#    for item in RD[subband]:
#        while subband != None:
#            print("{}\t{}\t{}".format(item[0], item[1], item[2]), sep='\t', end='\t')

RD = {}

# 3. For each subband in z (that is the same that in v):
subbands = os.listdir("/tmp/zero/")
for s in subbands:
    RD[s] = []
    rates = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
    for q_step in [(1 << i) for i in rates]:

        if __debug__:
            print(s, "in", subbands, q_step, "i", [(1 << i) for i in rates])
        
        # 3.1.1. Copy the subband s to the zero MCDWT sequence z.
        run("cp " + args.prefix + s + " /tmp/zero/")
        
        # 3.1.2. Quantize the subband s using q_step.
        run("python3 quantize.py -i /tmp/zero/" + s + " -o " + "/tmp/zero/" + s + " -q " + str(q_step))

        # 3.1.3. Compute the length of the subband quantized subband s.
        R = os.path.getsize("/tmp/zero/" + s)
        
        # 3.1.4. Reconstruct the video from z.
        run("python3 -O ../src/MCDWT.py -b -p /tmp/zero/ -N " + str(args.decompositions) + " -T " + str(args.iterations))
        run("python3 -O ../src/MDWT.py -b -p /tmp/zero/ -N " + str(args.decompositions))
        
        # 3.1.5. Compute the distortion between the original video and the reconstruction.
        D = 0.0
        for i in range(args.decompositions):
            ii = "{:03d}".format(i)
            original_image = args.originals + ii + ".png"
            reconstructed_image = "/tmp/zero/" + ii + ".png"
            MSE = float(run("python3 -O ./MSE.py" + " -x " + original_image + " -y " + reconstructed_image))
            D += MSE
            if __debug__:
                print(MSE)
        run("rm /tmp/zero/???.png") # Delete the images (keep the subbands)

        D /= args.decompositions
        RD[s].append((q_step, D,R))
        if __debug__:
            for i in RD:
                print(i, RD[i])

        # 3.1.6. Set to zero all z subbands.
        for ss in os.listdir("/tmp/zero/"):
            run("python3 quantize.py -i /tmp/zero/" + ss + " -o " + "/tmp/zero/" + ss + " -q " + str(1<<30))

df = pd.DataFrame.from_dict(RD)
print(df)
df.to_csv("RD_zero.csv")

input()

# 1. Create the video structure.
run("mkdir " + args.prefix + "/original")
run("cp " + args.originals + "*.png " + args.prefix + "original")
run("python3 -O ../src/MDWT.py" + " -p " + args.prefix + "original -N " + str(args.decompositions))
run("python3 -O ../src/MCDWT.py" + " -p " + args.prefix + "original -N " + str(args.decompositions) + " -T " + str(args.iterations))

# 2. Do a copy (w) of the original video.
run("cp -r " + args.prefix + "/original " + args.prefix)

RD = {}

# 3. For each subband in v:
subbands = os.listdir("/tmp/original/")
for s in subbands:
    RD[s] = []
    log2_rates = (16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0)
    for q_step in [(1 << i) for i in log2_rates]:

        if __debug__:
            print(s, "in", subbands, q_step, "i", [(1 << i) for i in log2_rates])
        
        # 3.1.1. Restore the working copy.
        run("cp /tmp/original/*" + s + " /tmp/")
        
        # 3.1.2. Quantize the subband s in w using q_step.
        run("python3 quantize.py -i /tmp/" + s + " -o " + "/tmp/" + s + " -q " + str(q_step))

        # 3.1.3. Compute the length of the quantized subband s.
        R = os.path.getsize("/tmp/" + s)
        
        # 3.1.4. Reconstruct the video from w.
        run("python3 -O ../src/MCDWT.py" + " -p " + args.prefix + " -N " + str(args.decompositions) + " -T " + str(args.iterations) + " -b")
        run("python3 -O ../src/MDWT.py" + " -p " + args.prefix + " -N " + str(args.decompositions) + " -b")
        
        # 3.1.5. Compute the distortion between v and v'.
        D = 0.0
        for i in range(args.decompositions):
            ii = "{:03d}".format(i)
            original_image = args.originals + ii + ".png"
            reconstructed_image = args.prefix + ii + ".png"
            MSE = float(run("python3 -O ./MSE.py" + " -x " + original_image + " -y " + reconstructed_image))
            D += MSE
            if __debug__:
                print(MSE)
        D /= args.decompositions
        RD[s].append((q_step, D,R))
        if __debug__:
            for i in RD:
                print(i, RD[i])

df = pd.DataFrame.from_dict(RD)
print(df)
df.to_csv("RD_originals.csv")

input()

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
              
              
