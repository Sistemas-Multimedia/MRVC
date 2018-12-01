#!/usr/bin/env python3

import os
import sys
import cv2
import numpy as np
import tempfile as tf
#sys.path.insert(0, '../mcdwt')
import argparse
from argparse import RawTextHelpFormatter

#Algorithms call functions
def algorithm_duplicator(frames):
    duplicator = __import__("duplicator")
    return duplicator.framerate_duplicator(frames)

#Algorithms dictionary
options = {
    0: algorithm_duplicator
}
#Resolve arguments
parser = argparse.ArgumentParser(description='Temporal interpolation.', formatter_class=RawTextHelpFormatter)
parser.add_argument('-a', type=int, default=0,
                    help="Algorithm to use (Default: 0)\n\t0: Duplicator\n\tMore in the future")

args = parser.parse_args()

#Main
n = 5
input_path = '../../images'
output_path = tf.gettempdir()

frames = []
for i in range(n):
    path = os.path.join(input_path, '{:03d}.png'.format(i))
    print('Reading frame:', path)
    frames.append(cv2.imread(path))

output = options[args.a](frames)

for i in range(len(output)):
    path = os.path.join(output_path, 'duplicator_{:02d}.png'.format(i))
    print('Writing frame:', path)
    cv2.imwrite(path, output[i])
