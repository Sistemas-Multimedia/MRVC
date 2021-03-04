''' MRVC/motion.py '''

import cv2
import numpy as np
import config

# Number of levels of the gaussian pyramid used in the Farneback's
# optical flow computation algorith (OFCA). This value controls the
# search area size.
#optical_flow_pyramid_levels = 3
optical_flow_pyramid_levels = 5

# Window size used in the Farneback's OFCA. This value controls the
# coherence of the OF.
#optical_flow_window_size = 5
optical_flow_window_size = 33

# Number of iterations of the Farneback's OFCA. This value controls
# the accuracy of the OF.
#optical_flow_iterations = 3
optical_flow_iterations = 5

# Signal extension mode used in the OFCA. See https://docs.opencv.org/3.4/d2/de8/group__core__array.html
ofca_extension_mode = cv2.BORDER_CONSTANT
#ofca_extension_mode = cv2.BORDER_WRAP
#ofca_extension_mode = cv2.BORDER_DEFAULT
#ofca_extension_mode = cv2.BORDER_REPLICATE
#ofca_extension_mode = cv2.BORDER_REFLECT
#ofca_extension_mode = cv2.BORDER_REFLECT_101
#ofca_extension_mode = cv2.BORDER_TRANSPARENT
#ofca_extension_mode = cv2.BORDER_REFLECT101
#ofca_extension_mode = BORDER_ISOLATED

print("OFCA extension mode =", ofca_extension_mode)

def estimate(predicted: np.ndarray, reference: np.ndarray, flow: np.ndarray =None) -> np.ndarray:
    flow = cv2.calcOpticalFlowFarneback(
        prev=predicted,
        next=reference,
        flow=flow,
        pyr_scale=0.5,
        levels=optical_flow_pyramid_levels,
        winsize=optical_flow_window_size,
        iterations=optical_flow_iterations,
        poly_n=5,
        poly_sigma=1.2,
        flags=0)
    return flow

def make_prediction(reference: np.ndarray, flow: np.ndarray) -> np.ndarray:
    height, width = flow.shape[:2]
    map_x = np.tile(np.arange(width), (height, 1))
    map_y = np.swapaxes(np.tile(np.arange(height), (width, 1)), 0, 1)
    map_xy = (flow + np.dstack((map_x, map_y))).astype('float32')
    return cv2.remap(reference, map_xy, None, interpolation=cv2.INTER_LINEAR, borderMode=ofca_extension_mode)
