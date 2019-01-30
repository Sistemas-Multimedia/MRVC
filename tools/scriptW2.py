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
sys.path.insert(0, "..")
from src.MC.optical.motion import generate_prediction
import src.DWT
import src.IO
import src.MC

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

    # Downloads the video
    print("Atempting to download video ...\n\n")
    subprocess.run("wget /tmp/{} ".format(videoPath) , shell=True, check=True)
    ##### Renames the video ####
    if videoName != "un_heliostato":
        subprocess.run("mv *.mp4 /tmp/{}.mp4".format(videoName), shell=True, check=True)  
    print("\n\nVideo Downloaded!\n\n")
    
    # Creates directories for the generated files
    subprocess.run("mkdir /tmp/{}".format(videoName), shell=True) # root directory
    subprocess.run("mkdir -p /tmp/{}/extracted".format(videoName), shell=True) # extracted frames from video
    subprocess.run("mkdir -p /tmp/{}/16bit".format(videoName), shell=True) # for the 16 bit transformed images
    subprocess.run("mkdir -p /tmp/{}/reconstructed".format(videoName), shell=True) # for the reconstructed images

    # Extracts the frames from video
    print("\n\nExtracting images ...\n\n")
    subprocess.run("ffmpeg -i /tmp/{}.mp4 -vframes {} /tmp/{}_%03d.png".format(videoName, nFrames, videoName), shell=True, check=True)
    subprocess.run("mv *.mp4 /tmp/{}".format(videoName), shell=True, check=True)
    subprocess.run("cp *.png /tmp/{}/extracted".format(videoName), shell=True, check=True)

    print("\n\n Done! ready to transform \n\n")

    # Convert the images to 16 bit
    for image in range(int(nFrames)):
        inputImg = ("/tmp/{}_{:03d}.png".format(videoName ,image+1))
        outputImg = ("/tmp/{:03d}.png".format(image+1))
        imgTo16(inputImg , outputImg)

    # Moves 16 bits images to the specific folder
    subprocess.run("cp 0* {}/16bit".format(videoName), shell=True, check=True)
    #subprocess.run("mkdir -p /tmp/{}".format(videoName), shell=True)
    #subprocess.run("cp 0* /tmp/{}".format(videoName), shell=True, check=True)
    

    ##########################################################

    ########## ADD Here the Convertion MCDWT #################

    # Motion 2D 1-levels forward DWT of the ’stockholm’ sequence:  
    subprocess.run("python3 -O ../src/MDWT.py -i /tmp/{}/ -d /tmp/heliostato/".format(videoName), shell=True, check=True)
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
    

def forward_butterfly(self, aL, aH, bL, bH, cL, cH): 
    AL = self.dwt.backward((aL, self.zero_H)) 
    BL = self.dwt.backward((bL, self.zero_H)) 
    CL = self.dwt.backward((cL, self.zero_H)) 
    AH = self.dwt.backward((self.zero_L, aH)) 
    BH = self.dwt.backward((self.zero_L, bH)) 
    CH = self.dwt.backward((self.zero_L, cH)) 
    BHA = self.dwt.generate_prediction(AL, BL, AH) 
    BHC = self.generate_prediction(CL, BL, CH) 
    prediction_BH = (BHA + BHC) / 2 
    residue_BH = BH - prediction_BH 
    residue_bH = self.dwt.forward(residue_BH) 
    return residue_bH[1]

def backward_butterfly(self, aL, aH, bL, residue_bH, cL, cH): 
    AL = self.dwt.backward((aL, self.zero_H)) 
    BL = self.dwt.backward((bL, self.zero_H)) 
    CL = self.dwt.backward((cL, self.zero_H)) 
    AH = self.dwt.backward((self.zero_L, aH)) 
    residue_BH = self.dwt.backward((self.zero_L, residue_bH)) 
    CH = self.dwt.backward((self.zero_L, cH)) 
    BHA = generate_prediction(AL, BL, AH) 
    BHC = generate_prediction(CL, BL, CH) 
    prediction_BH = (BHA + BHC) / 2 
    BH = residue_BH + prediction_BH 
    bH = self.dwt.forward(BH) 
    return bH[1]



if __name__ == "__main__":
    main()