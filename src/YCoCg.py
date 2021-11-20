''' MRVC/YCoCg.py '''

import numpy as np

name = "YCoCg"

def from_RGB(RGB_frame: np.ndarray) -> np.ndarray:
    assert RGB_frame.dtype != np.uint8
    assert RGB_frame.dtype != np.uint16
    #R, G, B = RGB_frame[0], RGB_frame[1], RGB_frame[2]
    R, G, B = RGB_frame[:,:,0], RGB_frame[:,:,1], RGB_frame[:,:,2]
    YCoCg_frame = np.empty_like(RGB_frame)
    YCoCg_frame[:,:,0] =  R/4 + G/2 + B/4 
    YCoCg_frame[:,:,1] =  R/2       - B/2
    YCoCg_frame[:,:,2] = -R/4 + G/2 - B/4
    return YCoCg_frame

def to_RGB(YCoCg_frame: np.ndarray) -> np.ndarray:
    #Y, Co, Cg = YCoCg_frame[0], YCoCg_frame[1], YCoCg_frame[2]
    Y, Co, Cg = YCoCg_frame[:,:,0], YCoCg_frame[:,:,1], YCoCg_frame[:,:,2]
    RGB_frame = np.empty_like(YCoCg_frame)
    RGB_frame[:,:,0] = Y + Co - Cg 
    RGB_frame[:,:,1] = Y      + Cg
    RGB_frame[:,:,2] = Y - Co - Cg
    return RGB_frame
