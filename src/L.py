''' MRVC/L.py '''

import numpy as np
import DWT
import cv2
from colors import red

def read(prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}LL{ASCII_frame_number}.png"
    subband = cv2.imread(fn, cv2.IMREAD_UNCHANGED) # [rows, columns, components]
    try:
        subband = cv2.cvtColor(subband, cv2.COLOR_BGR2RGB)
    except cv2.error:
        print(red(f'Unable to read "{fn}"'))
        raise
    subband = np.array(subband, dtype=np.float64)
    subband -= 32768.0
    return subband # [rows, columns, components]

def write(L, prefix, frame_number):
    subband = np.array(L, dtype=np.float64)
    subband += 32768.0
    subband = subband.astype(np.uint16)
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}LL{ASCII_frame_number}.png"
    print(subband.shape, fn)
    subband = cv2.cvtColor(subband, cv2.COLOR_RGB2BGR)
    cv2.imwrite(fn, subband)

def interpolate(L):
    LH = np.zeros(shape=L.shape, dtype=np.float64)
    HL = np.zeros(shape=L.shape, dtype=np.float64)
    HH = np.zeros(shape=L.shape, dtype=np.float64)
    H = (LH, HL, HH)
    _L_ = DWT.synthesize_step(L, H)
    return _L_

def reduce(_L_):
    L, _ = DWT.analyze_step(_L_)
    return L
