''' MRVC/YCrCb.py '''

import cv2
import numpy as np

def from_RGB(RGB_frame: np.ndarray) -> np.ndarray:
    # Remember that cv2.cvtColor only works with unsigneds!
    #RGB_frame = cv2.merge((RGB_frame[0], RGB_frame[1], RGB_frame[2]))
    #YCrCb_frame = cv2.cvtColor(np.clip(RGB_frame, 0, 255).astype(np.uint8), cv2.COLOR_RGB2YCR_CB)
    YCrCb_frame = cv2.cvtColor(RGB_frame, cv2.COLOR_RGB2YCR_CB)
    #YCrCb_frame = np.array(cv2.split(YCrCb_frame))
    return YCrCb_frame

def to_RGB(YCrCb_frame: np.ndarray) -> np.ndarray:
    #YCrCb_frame = cv2.merge((YCrCb_frame[0], YCrCb_frame[1], YCrCb_frame[2]))
    #RGB_frame = cv2.cvtColor(np.clip(YCrCb_frame, 0, 255).astype(np.uint8), cv2.COLOR_YCR_CB2RGB)
    RGB_frame = cv2.cvtColor(YCrCb_frame, cv2.COLOR_YCR_CB2RGB)
    #RGB_frame = np.array(cv2.split(RGB_frame))
    return RGB_frame
