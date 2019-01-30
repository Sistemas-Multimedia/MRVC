#!/usr/bin/env python3

# Note: swap the above line with the following two ones to switch
# between the standard and the optimized running mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

import numpy as np
import pywt
import math
import sys
import subprocess
import argparse
import cv2
import numpy

def main():
    
    # Creates the command line arguments 
    parser = argparse.ArgumentParser("Script for Issue Week 2")
    parser.add_argument("-vpath", help="Path to the video to download")
    parser.add_argument("-level", help="Number of spatial resolutions (levels in the Laplacian Pyramid)" ,default=1)
    parser.add_argument("-gop", help="number of temporal resolutions (GOP size)", default= 10)
    parser.add_argument("-vname", help="Name of the video")
    parser.add_argument("-frames", help="Number of frames to extract from video to transform")

    # Pareses all the arguments
    args = parser.parse_args()

    # Path to the video
    if args.vpath != None:
        videoPath = args.vpath
    else:
        videoPath = "http://www.hpca.ual.es/~vruiz/videos/un_heliostato.mp4"

    # Name of the video
    if args.vname != None:
        videoName = args.vname
    else:
        videoName = "un_heliostato"
    
    # Number of frames to be extracted
    if args.frames != None:
        nFrames = int(args.frames)
    else:
        nFrames = 5

    # Number of levels for the Laplacian Pyramid
    if args.level != None:
        nLevel = int(args.level)
    else:
        nLevel = 1

    # GOP size
    if args.gop != None:
        nGOP = args.gop
    else:
        nGOP = 10

    #source = os.listdir("/mnt/hgfs/Sistemas Multimedia/Exercise Git/MCDWT/tools/")
    #destination = "/tmp/"


    # Downloads the video
    print("Atempting to download video ...\n\n")
    subprocess.run("wget {} ".format(videoPath) , shell=True, check=True)
    ##### Renames the video ####
    if videoName != "un_heliostato":
        subprocess.run("mv *.mp4 {}.mp4".format(videoName), shell=True, check=True)  
    print("\n\nVideo Downloaded!\n\n")
    
    # Creates directories for the generated files
    subprocess.run("mkdir {}".format(videoName), shell=True) # root directory
    subprocess.run("mkdir -p {}/extracted".format(videoName), shell=True) # extracted frames from video
    subprocess.run("mkdir -p {}/16bit".format(videoName), shell=True) # for the 16 bit transformed images
    subprocess.run("mkdir -p {}/reconstructed".format(videoName), shell=True) # for the reconstructed images

    # Extracts the frames from video
    print("\n\nExtracting images ...\n\n")
    subprocess.run("ffmpeg -i {}.mp4 -vframes {} {}_%03d.png".format(videoName,nFrames, videoName), shell=True, check=True)
    subprocess.run("mv *.mp4 {}".format(videoName), shell=True, check=True)
    subprocess.run("cp *.png {}/extracted".format(videoName), shell=True, check=True)

    print("\n\n Done! ready to transform \n\n")

    # Convert the images to 16 bit
    for image in range(int(nFrames)):
        inputImg = ("{}_{:03d}.png".format(videoName ,image+1))
        outputImg = ("{:03d}.png".format(image+1))
        imgTo16(inputImg , outputImg)

    # Moves 16 bits images to the specific folder
    subprocess.run("cp 0* {}/16bit".format(videoName), shell=True, check=True)


    ##########################################################

    ########## ADD Here the Convertion MCDWT #################

    ##########################################################



    # Reconstruct 16bit images back to normal
    for image in range(int(nFrames)):
        inputImg = ("{:03d}.png".format(image+1))
        outputImg = ("reconstructed_{:03d}.png".format(image+1))
        imgReconstruct(inputImg , outputImg)

    # Moves reconstructed images to the specific folder
    subprocess.run("mv reconstructed* {}/reconstructed".format(videoName), shell=True, check=True)

    # Removes the generated files from the root folder
    subprocess.run("rm *.png", shell=True, check=True)


    """ for files in source:
        if files.endswith(".mp4") or files.endswith(".png"):
            shutil.move(files,destination)
            print ("Moved to tmp") """


def imgTo16(input, output):
    image = cv2.imread(input, -1).astype(np.uint16)
    print(np.amax(image), np.amin(image))
    image += (32768-128)
    print(np.amax(image), np.amin(image))
    cv2.imwrite(output, image.astype(np.uint16))


def imgReconstruct(input, output):
    image = cv2.imread(input, -1)
    image = np.clip(image, 32768-128, 32768-128+255)
    image -= (32768-128)
    cv2.imwrite(output, image.astype(np.uint8))
    





if __name__ == "__main__":
    main()