#!/usr/bin/env python

import cv2
import numpy as np
import argparse

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

parser = argparse.ArgumentParser(description = "Compress (lossy) image\n\n"
                                 "Example:\n\n"
                                 "  python -O compress.py -i ../sequences/stockholm/000.png -o /tmp/000.png -q 64\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--input", help="Input image", default="../sequences/stockholm/000.png")
parser.add_argument("-o", "--output", help="Output image", default="/tmp/000.png")
parser.add_argument("-q", "--quality", type=int, help="Quality", default=50)

args = parser.parse_args()
image = cv2.imread(args.input, -1)
image = image.astype(np.float32)
image -= 32768
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), args.quality]
_, jpg = cv2.imencode('.jpg', image, encode_param)
image = cv2.imdecode(jpg, 1)
cv2.imwrite(args.output, image)

