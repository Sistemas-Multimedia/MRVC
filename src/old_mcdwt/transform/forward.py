#!/usr/bin/env python

import argparse
import mcdwt

parser = argparse.ArgumentParser(description = "MCDWT forward transform")

parser.add_argument("-i", "--input",
                        help="Input images",
                        default="/tmp/")

parser.add_argument("-N", "--frames",
                        help="Number of images to encode",
                        default=5)

parser.add_argument("-K", "--temporal_levels",
                        help="Number of temporal levels",
                        default=2)

args = parser.parse_args()

mcdwt.forward(args.input, args.frames, args.temporal_levels)

