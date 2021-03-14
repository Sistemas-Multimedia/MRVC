''' MRVC/motion.py '''

import cv2 as cv
import numpy as np
import config

# Number of levels of the gaussian pyramid used in the Farneback's
# optical flow computation algorith (OFCA). This value controls the
# search area size.
#optical_flow_pyramid_levels = 3
optical_flow_pyramid_levels = 5
#optical_flow_pyramid_levels = 1

# Window size used in the Farneback's OFCA. This value controls the
# coherence of the OF.
#optical_flow_window_size = 5
optical_flow_window_size = 16

# Number of iterations of the Farneback's OFCA. This value controls
# the accuracy of the OF.
optical_flow_iterations = 3
#optical_flow_iterations = 5

# Signal extension mode used in the OFCA. See https://docs.opencv.org/3.4/d2/de8/group__core__array.html
#ofca_extension_mode = cv.BORDER_CONSTANT
#ofca_extension_mode = cv.BORDER_WRAP
#ofca_extension_mode = cv.BORDER_DEFAULT
ofca_extension_mode = cv.BORDER_REPLICATE
#ofca_extension_mode = cv.BORDER_REFLECT
#ofca_extension_mode = cv.BORDER_REFLECT_101
#ofca_extension_mode = cv.BORDER_TRANSPARENT
#ofca_extension_mode = cv.BORDER_REFLECT101
#ofca_extension_mode = cv.BORDER_ISOLATED

print("OFCA extension mode =", ofca_extension_mode)

def estimate(predicted:np.ndarray, reference:np.ndarray, reference_flow:np.ndarray=None) -> np.ndarray:
    flow = cv.calcOpticalFlowFarneback(
        prev=predicted,
        next=reference,
        #next=predicted,
        #prev=reference,
#        flow=reference_flow,
        flow=None,
        pyr_scale=0.5,
        levels=optical_flow_pyramid_levels,
        winsize=optical_flow_window_size,
        iterations=optical_flow_iterations,
        poly_n=7,
        poly_sigma=1.5,
        #flags=cv.OPTFLOW_FARNEBACK_GAUSSIAN)
        flags=0)
        #flags=cv.OPTFLOW_USE_INITIAL_FLOW|cv.OPTFLOW_FARNEBACK_GAUSSIAN)
        #flags=cv.OPTFLOW_USE_INITIAL_FLOW)
    return flow

def make_prediction(reference: np.ndarray, flow: np.ndarray) -> np.ndarray:
    height, width = flow.shape[:2]
    map_x = np.tile(np.arange(width), (height, 1))
    map_y = np.swapaxes(np.tile(np.arange(height), (width, 1)), 0, 1)
    #map_xy = (flow + np.dstack((map_x, map_y))).astype('float32')
    map_xy = (np.rint(flow) + np.dstack((map_x, map_y)).astype(np.float32))
    return cv.remap(reference, map_xy, None, interpolation=cv.INTER_LINEAR, borderMode=ofca_extension_mode)
    #return cv.remap(reference, map_xy, None, interpolation=cv.INTER_NEAREST, borderMode=ofca_extension_mode)
    
    #return cv.remap(reference, cv.convertMaps(map_x, map_y, dstmap1type=cv.CV_16SC2), interpolation=cv.INTER_LINEAR, borderMode=ofca_extension_mode)
    #return cv.remap(reference, map_x, map_y, interpolation=cv.INTER_LINEAR, borderMode=ofca_extension_mode)

def colorize(flow):
    hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
    hsv[...,1] = 255
    mag, ang = cv.cartToPolar(flow[...,0], flow[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)
    rgb = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    return rgb
