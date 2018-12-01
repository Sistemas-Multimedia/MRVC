#!/usr/bin/env python3

import numpy as np
import cv2
import pywt
import argparse
from transform import mcdwt

parser = argparse.ArgumentParser(description='video cam recorder')
parser.add_argument('--width', dest='width', help='width', required=True)
parser.add_argument('--height', dest='height', help='height', required=True)
parser.add_argument('--fps', dest='fps', help='fps', required=True)
parser.add_argument('--out', dest='out', help='out', required=True)
args = parser.parse_args()

width = int(args.width)
height = int(args.height)

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(args.out ,fourcc, float(args.fps), (width, height), False)

l = 1

cache = []
first_time = True

while(cap.isOpened()):
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
  
    if ret==True:
        if len(cache) == 2*l:
            A, B, C = mcdwt.forward(cache[0], cache[1], frame)
            out.write(np.uint8(B))
            out.write(np.uint8(C))
            cache = []
            if first_time:
                out.write(np.uint8(A))
                first_time = False
        cache.append(frame)
    else:
        break
out.release()
