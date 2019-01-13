import numpy as np
import cv2

def generate_prediction(curr, next, base):
    flow = motion_estimation(curr, next)
    return estimate_frame(base, flow)

def motion_estimation(curr, next):
    curr_y, _, _ = cv2.split(curr)
    next_y, _, _ = cv2.split(next)

    return cv2.calcOpticalFlowFarneback(next_y, curr_y, 
            None, 0.5, 3, 15, 3, 5, 1.2, 0)

def estimate_frame(base, flow):
    height, width = flow.shape[:2]
    map_x = np.tile(np.arange(width), (height, 1))
    map_y = np.swapaxes(np.tile(np.arange(height), (width, 1)), 0, 1)
    map_xy = (flow + np.dstack((map_x, map_y))).astype('float32')

    return cv2.remap(base, map_xy, None, 
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE)
