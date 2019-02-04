#!/usr/bin/env python3

# Note: swap the above line with the following two ones to switch
# between the standard and the optimized running mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

"""png_to_video.py: Converts the reconstructed 16 bit images in 000 format to 000.png normalized to export as a video."""

import numpy as np
import subprocess
import argparse


def main():

    # Creates the command line arguments
    parser = argparse.ArgumentParser("Converts png images in format 000.png to video")
    parser.add_argument("-i", help="path to the .png images")
    parser.add_argument("-frames", help="Number of frames to convert", default = 5)
    parser.add_argument("-o", help="Path to export the video", default = "video.mp4")
    parser.add_argument("-addextension", help="if images are in format 000 without extension")

    # Parses all the arguments
    args = parser.parse_args()

    # Path to images
    if args.i != None:
        inputPath = args.i
    else:
        inputPath = "/tmp/"

    # If needs to add .png extension
    if args.addextension != None:
        add_extension = True
    else:
        add_extension = False
        
    # Number of frames
    if args.frames != None:
        nFrames = int(args.frames)
    else:
        nFrames = 5

    # Reconstruct 16bit original images back to noramlized and .png extension
    for image in range(int(nFrames)):
        inputImg = ("{}{:03d}".format(inputPath, image))
        outputImg = ("{}{:03d}.png".format(inputPath ,image))
        subprocess.run("python3 substract_offset.py -i {} -o {}".format(inputImg, outputImg), shell=True, check=True)
        #subprocess.run("rm -f -i {}{:03d}".format(inputPath, image), shell=True, check=True)

    # Creates the video with the .png images
    subprocess.run("ffmpeg -i {}%03d.png  {}video.mp4".format( inputPath, inputPath), shell=True, check=True)
    

if __name__ == "__main__":
    main()
