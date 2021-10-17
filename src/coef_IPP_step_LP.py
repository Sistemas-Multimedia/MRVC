''' MRVC/coef_IPP_step_LP.py '''

import numpy as np
#import DWT as spatial_transform
import LP as spatial_transform
#import L_DWT as L
import L_LP as L
#import H_DWT as H
import H_LP as H
import deadzone_quantizer as Q
import motion
import frame
import colors
import cv2
import os
import coef_IPP_step

def encode(video, n_frames, q_step):
    coef_IPP_step.encode(video, n_frames, q_step)
