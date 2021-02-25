''' MRVC/motion.py '''

import cv2
import numpy as np

def estimate(predicted: np.ndarray, reference: np.ndarray, flow: np.ndarray =None) -> np.ndarray:
    flow = cv2.calcOpticalFlowFarneback(
        prev=predicted,
        next=reference,
        flow=flow,
        pyr_scale=0.5,
        levels=3,
        winsize=7,
        iterations=3,
        poly_n=5,
        poly_sigma=1.2,
        flags=0)
    return flow

def make_prediction(reference: np.ndarray, flow: np.ndarray) -> np.ndarray:
    height, width = flow.shape[:2]
    map_x = np.tile(np.arange(width), (height, 1))
    map_y = np.swapaxes(np.tile(np.arange(height), (width, 1)), 0, 1)
    map_xy = (flow + np.dstack((map_x, map_y))).astype('float32')
    return cv2.remap(reference, map_xy, None, 
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE)
