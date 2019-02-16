#!/usr/bin/env python3

# Note: swap the above line with the following two ones to switch
# between the standard and the optimized running mode.

#!/bin/sh
''''exec python3 -O -- "$0" ${1+"$@"} # '''

"""scriptv2.py: video DMCWT multi-level transform and reconstruction utility."""

# course: Multimedia Systems
# Issue: 1
# date: 2019
# username: dbc770
# name: David Béjar Cáceres
# description: video DMCWT multi-level direct transform and reconstruction utility.

import numpy as np
import pywt
import math
import sys
import subprocess
import argparse
import cv2
import numpy
sys.path.insert(0, "..")
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
    parser.add_argument("-T", help="Number of levels of the MCDWT (temporal scales)")
    parser.add_argument("-vname", help="Name of the folder and video to export in tmp folder")
    parser.add_argument("-transform", help="True direct transform / False to reconstruct", default="True")

    # Parses all the arguments
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
        videoName = "video_transformed"

    # Number of frames to be extracted
    if args.frames != None:
        nFrames = int(args.frames)
    else:
        nFrames = 5

    # Number of T
    if args.T != None:
        t_scale = int(args.T)
    else:
        t_scale = 2

    # Number of levels for the Laplacian Pyramid
    if args.level != None:
        nLevel = int(args.level)
    else:
        nLevel = 1

    # Check the flag to direct transform
    if args.transform != None:
        transform = str(args.transform)
    else:
        transform = str(True)

    if transform == "True":
        # Creates directories for the generated files
        subprocess.run("mkdir /tmp/{}".format(videoName), shell=True) # root directory
        subprocess.run("mkdir -p /tmp/{}/extracted".format(videoName), shell=True) # extracted frames from video
        subprocess.run("mkdir -p /tmp/{}/16bit".format(videoName), shell=True) # for the 16 bit transformed images
        subprocess.run("mkdir -p /tmp/{}/reconstructed".format(videoName), shell=True) # for the reconstructed 16 bit original images
        # subprocess.run("mkdir -p /tmp/{}/MDWT".format(videoName), shell=True) # images after MDWT
        # subprocess.run("mkdir -p /tmp/{}/MDWT/MCDWT".format(videoName), shell=True) # images after MCDWT
        # subprocess.run("mkdir -p /tmp/{}/MDWT/MCDWT/1".format(videoName), shell=True) # images after MCDWT
        # subprocess.run("mkdir -p /tmp/{}/_reconMCDWT".format(videoName), shell=True) # Recons backwards from MCDWT
        # subprocess.run("mkdir -p /tmp/{}/_reconMDWT".format(videoName), shell=True) # Reconstruct backwards from MCWT

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
            subprocess.run("python3 add_offset.py -i {} -o {}".format(inputImg, outputImg), shell=True, check=True)

        # delete extensions from 16 bit images
        # for image in range(int(nFrames)):
        #     subprocess.run("mv /tmp/{}/16bit/{:03d}.png /tmp/{}/16bit/{:03d}".format(videoName, image, videoName, image), shell=True, check=True)

        print("\n Removed extensions from 16 bit images...\n")
        print("\nDone! ready to transform \n")

        ########## MDWT Transform #################
        # Motion 2D 1-levels forward DWT of the frames from the video:
        subprocess.run("python3  ../src/MDWT.py -p /tmp/{}/16bit/  -N {}".format(videoName, nFrames), shell=True, check=True)
        print("\nFirst transform MDWT done!")

        ########## MCDWT Transform #################
        # Motion Compensated 1D 1-levels forward MCDWT:
        subprocess.run("python3 -O ../src/MCDWT.py -p /tmp/{}/16bit/ -N {} -T {}".format(videoName, nFrames, t_scale), shell=True, check=True)
        print("\nTransform MCDWT done!")

        newLevel = "" # Stores the last level of the MCDWT

        # Support for multi-level forwards MCDWT
        if nLevel > 1:
            print("\nWorking on multi-level MCDWT...")
            mlevelpath = "/tmp/{}/MDWT/MCDWT/".format(videoName)
            for i in range(nLevel-1):
                print("Nivel {}".format(i+2))
                newLevel = ("{}/{}".format(mlevelpath, str(i+2)))
                subprocess.run("mkdir -p {}".format(newLevel), shell=True) # creates next level MCDWT dir
                # Works on the last MCDWT and transform to the new level
                subprocess.run("python3 -O ../src/MCDWT.py -d {}{}/ -m {}{}/ -N {} -T {}".format(mlevelpath, i+1 , mlevelpath, i+2 , nFrames, t_scale), shell=True, check=True)

            print("Last level of MCDWT located in:  {}".format(newLevel))

    if transform == "False":
        ######## Reconstruction #########
        # Support for multi-level backwards reconstruction MCDWT
        if nLevel > 1:
            print("\nReconstructing multi-level MCDWT...")
            mlevelMCDWT = "/tmp/{}/MDWT/MCDWT/".format(videoName)
            mlevelrecons = ("/tmp/{}/_reconMCDWT/".format(videoName))
            for i in reversed(range(nLevel-1)):
                subprocess.run("mkdir -p {}{}".format(mlevelrecons, i+1 ), shell=True) # creates next level MCDWT dir
                # Reconstructs form the last MCDWT level
                subprocess.run("python3 -O ../src/MCDWT.py -b -m {}{}/ -d {}{}/ -N {} -T {}".format(mlevelMCDWT, i+2 , mlevelrecons, i+1, nFrames-1, t_scale), shell=True, check=True)
                print("Reconstructed from MCDWT level {} done!".format(i+2))

            print("\nMulti-levels reconstructed...\n")
        else:
            # Reconstructs form the last MCDWT level
                print("\nReconstructed from level MCDWT")
        subprocess.run("python3 -O ../src/MCDWT.py -p /tmp/{}/16bit/ -b -N {} -T {}".format(videoName, nFrames, t_scale), shell=True, check=True)

        # Motion 2D 1-levels backward DWT:
        subprocess.run("python3  ../src/MDWT.py -p /tmp/{}/16bit/ -b  -N {}".format(videoName, nFrames), shell=True, check=True)
        print("\nReconstructed from MDWT done!")
        print("\nCheck reconstructed sequence in: /tmp/{}/_reconMDWTcon".format(videoName))

        # Reconstruct 16bit original images back to normal
        for image in range(int(nFrames)):
            inputImg = ("/tmp/{}/16bit/{:03d}.png".format(videoName, image))
            outputImg = ("/tmp/{}/reconstructed/{:03d}.png".format(videoName ,image))
            subprocess.run("python3 substract_offset.py -i {} -o {}".format(inputImg, outputImg), shell=True, check=True)

        print("Check results on /tmp/{} folder".format(videoName))
        print("\n\nScript Finished!")

if __name__ == "__main__":
    main()
