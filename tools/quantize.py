#!/usr/bin/env python

import os
import argparse
try:
    import cv2
except:
    os.system("pip3 install opencv-python --user")
try:
    import numpy as np
except:
    os.system("pip3 install numpy -user")

def quantize(input, q_step):
    if __debug__:
        print("q_step = {}".format(q_step))
        print("Max value at input = {}".format(np.amax(input)))
        print("Min value at input = {}".format(np.amin(input)))
    output = (input/q_step).astype(np.int16)*q_step
    if __debug__:
        print("Max value at output = {}".format(np.amax(output)))
        print("Min value at output = {}".format(np.amin(output)))
    return output

def run(input, output, q_step):
    image = cv2.imread(input, -1)
    tmp = image.astype(np.float32)
    tmp -= 32768

    if __debug__:
        print("\nInput image = {}".format(input))
        print("Output image = {}".format(output))

    image = quantize(tmp, q_step)

    tmp = image.astype(np.float32)
    tmp += 32768
    image = tmp.astype(np.uint16)

    cv2.imwrite(output, image)

def main():

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

    parser = argparse.ArgumentParser(description = "Quantize an image\n\n"
                                     "Example:\n\n"
                                     "  python -O quantize.py -i ../sequences/stockholm/000.png -o /tmp/000.png -q 64\n",
                                     formatter_class=CustomFormatter)

    parser.add_argument("-i", "--input", help="Input image", default="../sequences/stockholm/000.png")
    parser.add_argument("-o", "--output", help="Output image", default="/tmp/000.png")
    parser.add_argument("-q", "--q_step", type=int, help="Quantization step", default=32)

    args = parser.parse_args()
    run(args.input, args.output, args.q_step)

if __name__ == "__main__":
    main()
