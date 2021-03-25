''' MRVC/motion.py '''

import cv2
import numpy as np
import config

###########################################################################
# OF section. See:                                                        #
# https://www.geeksforgeeks.org/opencv-the-gunnar-farneback-optical-flow/ #
###########################################################################

# Number of levels of the gaussian pyramid used in the Farneback's
# optical flow computation algorith (OFCA). This value controls the
# search area size.
OF_LEVELS = 3
print("OFCA: default number of levels =", OF_LEVELS)

# Window (squared) side used in the Farneback's OFCA. This value controls the
# coherence of the OF.
OF_WINDOW_SIDE = 33
print(f"OFCA: default window size = {OF_WINDOW_SIDE}x{OF_WINDOW_SIDE}")

# Number of iterations of the Farneback's OFCA. This value controls
# the accuracy of the OF.
OF_ITERS = 3
print(f"OFCA: default number of iterations =", OF_ITERS)

# Signal extension mode used in the OFCA. See https://docs.opencv.org/3.4/d2/de8/group__core__array.html
#ofca_extension_mode = cv2.BORDER_CONSTANT
#ofca_extension_mode = cv2.BORDER_WRAP
#ofca_extension_mode = cv2.BORDER_DEFAULT
ofca_extension_mode = cv2.BORDER_REPLICATE
#ofca_extension_mode = cv2.BORDER_REFLECT
#ofca_extension_mode = cv2.BORDER_REFLECT_101
#ofca_extension_mode = cv2.BORDER_TRANSPARENT
#ofca_extension_mode = cv2.BORDER_REFLECT101
#ofca_extension_mode = BORDER_ISOLATED
print("OFCA: extension mode =", ofca_extension_mode)

#POLY_N = 5
#POLY_SIGMA = 1.1
POLY_N = 7
POLY_SIGMA = 1.5
print("OFCA: default poly_n", POLY_N)
print("OFCA: default poly_sigma", POLY_SIGMA)

def estimate(predicted:np.ndarray,
             reference:np.ndarray,
             initial_flow:np.ndarray=None,
             levels:int=OF_LEVELS,
             wside:int=OF_WINDOW_SIDE,
             iters:int=OF_ITERS,
             poly_n:float=POLY_N,
             poly_sigma:float=POLY_SIGMA) -> np.ndarray:
    print("estimate: levels =", levels)
    print("estimate: wside =", wside)
    print("estimate: iters =", iters)
    print("estimate: poly_n =", poly_n)
    print("estimate: poly_sigma =", poly_sigma)
    flow = cv2.calcOpticalFlowFarneback(
        prev=predicted,
        next=reference,
        flow=initial_flow,
        pyr_scale=0.5,
        levels=levels,
        winsize=wside,
        iterations=iters,
        poly_n=5,
        poly_sigma=1.2,
        flags=cv2.OPTFLOW_USE_INITIAL_FLOW | cv2.OPTFLOW_FARNEBACK_GAUSSIAN)
    return flow

def make_prediction(reference: np.ndarray, flow: np.ndarray) -> np.ndarray:
    height, width = flow.shape[:2]
    map_x = np.tile(np.arange(width), (height, 1))
    map_y = np.swapaxes(np.tile(np.arange(height), (width, 1)), 0, 1)
    #map_xy = (flow + np.dstack((map_x, map_y))).astype('float32')
    map_xy = (np.rint(flow) + np.dstack((map_x, map_y)).astype(np.float32)) # OJO RINT
    return cv2.remap(reference, map_xy, None, interpolation=cv2.INTER_LINEAR, borderMode=ofca_extension_mode)
    #return cv2.remap(reference, map_xy, None, interpolation=cv2.INTER_NEAREST, borderMode=ofca_extension_mode)
    
    #return cv2.remap(reference, cv2.convertMaps(map_x, map_y, dstmap1type=cv2.CV_16SC2), interpolation=cv2.INTER_LINEAR, borderMode=ofca_extension_mode)
    #return cv2.remap(reference, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=ofca_extension_mode)

def colorize(flow):
    hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
    hsv[...,1] = 255
    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return rgb
