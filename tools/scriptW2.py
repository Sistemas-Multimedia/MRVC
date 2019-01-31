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
    parser.add_argument("-vpath", help="Path to the local video, with .mp4 extension")
    parser.add_argument("-vurl", help="URL to the video to download")
    parser.add_argument("-level", help="Number of spatial resolutions (levels in the Laplacian Pyramid)" ,default=1)
    parser.add_argument("-frames", help="Number of frames to extract from video to transform")
    parser.add_argument("-gop", help="number of temporal resolutions (GOP size)", default= 10)
    parser.add_argument("-vname", help="Name of the folder and video to export in tmp folder")
    

    # Pareses all the arguments
    args = parser.parse_args()

    # URL to the video
    if args.vurl != None:
        videoURL = args.vurl
    else:
        videoURL = "http://www.hpca.ual.es/~vruiz/videos/un_heliostato.mp4"

    # Path to the video in local
    if args.vpath != None:
        videoPath = args.vpath
        localVideo = True
    else:
        localVideo = False

    # Name of the video
    if args.vname != None:
        videoName = args.vname
    else:
        videoName = "videoTransformed"
    
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

    # Creates directories for the generated files
    subprocess.run("mkdir /tmp/{}".format(videoName), shell=True) # root directory
    subprocess.run("mkdir -p /tmp/{}/extracted".format(videoName), shell=True) # extracted frames from video
    subprocess.run("mkdir -p /tmp/{}/16bit".format(videoName), shell=True) # for the 16 bit transformed images
    subprocess.run("mkdir -p /tmp/{}/reconstructed".format(videoName), shell=True) # for the reconstructed images
    subprocess.run("mkdir -p /tmp/{}/MDWT".format(videoName), shell=True) # images after MDWT
    subprocess.run("mkdir -p /tmp/{}/MDWT/MCDWT".format(videoName), shell=True) # images after MCDWT
    subprocess.run("mkdir -p /tmp/{}/_reconMCDWT".format(videoName), shell=True) # Recons backwards from MCDWT
    subprocess.run("mkdir -p /tmp/{}/_reconMDWT".format(videoName), shell=True) # Reconstruct backwards from MCWT

    # Working with videos from the web
    if localVideo != True:
        # Downloads the video
        print("Atempting to download video ...\n\n")
        subprocess.run("wget {} -O /tmp/{}/{}.mp4 ".format(videoURL, videoName, videoName) , shell=True, check=True)
        print("\n\nVideo Downloaded!\n\n")
    
    # Working with local video
    if localVideo:
        subprocess.run("mv {} /tmp/{}/{}.mp4".format(videoPath,videoName, videoName), shell=True, check=True)  


    # Extracts the frames from video
    print("\n\nExtracting images ...\n\n")
    subprocess.run("ffmpeg -i /tmp/{}/{}.mp4 -vframes {} /tmp/{}/extracted/{}_%03d.png".format(videoName, videoName,  nFrames,videoName,  videoName), shell=True, check=True)

    # Convert the images to 16 bit
    for image in range(int(nFrames)):
        inputImg = ("/tmp/{}/extracted/{}_{:03d}.png".format(videoName, videoName ,image+1))
        outputImg = ("/tmp/{}/16bit/{:03d}.png".format(videoName, image))
        imgTo16(inputImg , outputImg)
    
    # delete extensions from 16 bit images
    for image in range(int(nFrames)):
        subprocess.run("mv /tmp/{}/16bit/{:03d}.png /tmp/{}/16bit/{:03d}".format(videoName, image, videoName, image), shell=True, check=True)
    
    print("\n Removed extensions from 16 bit images...\n")
    print("\nDone! ready to transform \n")

    ########## MDWT Transform #################
    # Motion 2D 1-levels forward DWT of the frames from the video:  
    subprocess.run("python3 -O ../src/MDWT.py -i /tmp/{}/16bit/ -d /tmp/{}/MDWT/ -N {}".format(videoName, videoName, nFrames), shell=True, check=True)
    print("\nFirst transform MDWT done!")

    
    ########## MCDWT Transform #################
    # Motion Compensated 1D 1-levels forward DWT:
    subprocess.run("python3 -O ../src/MCDWT.py -d /tmp/{}/MDWT/ -m /tmp/{}/MDWT/MCDWT/ -N {}".format(videoName, videoName, nFrames-1), shell=True, check=True)
    print("\nTransform MCDWT done!")


    ##### Reconstructs from the MCDWT Transform ######
    # Motion Compensated 1D 1-levels backward DWT:
    subprocess.run("python3 -O ../src/MCDWT.py -b -m /tmp/{}/MDWT/MCDWT/ -d /tmp/{}/_reconMCDWT/ -N {}".format(videoName, videoName, nFrames-1), shell=True, check=True)
    print("\nReconstructed from MCDWT done!")

    # Motion 2D 1-levels backward DWT:  
    subprocess.run("python3 -O ../src/MDWT.py -b -d /tmp/{}/_reconMCDWT/ -i /tmp/{}/_reconMDWT/  -N {}".format(videoName, videoName, nFrames-1), shell=True, check=True)
    print("\nReconstructed from MDWT done!")

    
    if nLevel > 1:
        print("Trabajando con transformaciones multi-nivel")

    
    # Reconstruct 16bit images back to normal
    for image in range(int(nFrames)):
        inputImg = ("/tmp/{}/16bit/{:03d}".format(videoName, image))
        outputImg = ("/tmp/{}/reconstructed/reconstructed_{:03d}.png".format(videoName ,image))
        imgReconstruct(inputImg , outputImg)

    print("\nCheck results on tmp/{} folder".format(videoName))
    print("\n\n Script Finished!")



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

def MDWTtoFolders():
    # if called, all the MDWT images are moved to specific folders
    subprocess.run("mkdir -p /tmp/{}/MDWT/LL".format(videoName), shell=True) # for LL Band images
    subprocess.run("mkdir -p /tmp/{}/MDWT/LH".format(videoName), shell=True) # for LH Band images
    subprocess.run("mkdir -p /tmp/{}/MDWT/HL".format(videoName), shell=True) # for HL Band images
    subprocess.run("mkdir -p /tmp/{}/MDWT/HH".format(videoName), shell=True) # for HH Band images

    subprocess.run("mv /tmp/{}/MDWT/*_LL /tmp/{}/MDWT/LL/".format(videoName, videoName ), shell=True, check=True)
    subprocess.run("mv /tmp/{}/MDWT/*_LH /tmp/{}/MDWT/LH/".format(videoName, videoName ), shell=True, check=True)
    subprocess.run("mv /tmp/{}/MDWT/*_HL /tmp/{}/MDWT/HL/".format(videoName, videoName ), shell=True, check=True)
    subprocess.run("mv /tmp/{}/MDWT/*_HH /tmp/{}/MDWT/HH/".format(videoName, videoName ), shell=True, check=True)




if __name__ == "__main__":
    main()