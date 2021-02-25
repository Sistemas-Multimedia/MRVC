''' MRVC/H.py '''

import numpy as np
import DWT
import cv2
import colors
if __debug__:
    import os

def read(prefix: str, frame_number: int) -> tuple: # [LH, HL, HH], each one [rows, columns, components]
    ASCII_frame_number = str(frame_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    H = []
    sb = 0
    for sbn in subband_names:
        fn = f"{prefix}{sbn}{ASCII_frame_number}.png"
        subband = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
        try:
            subband = cv2.cvtColor(subband, cv2.COLOR_BGR2RGB)
        except cv2.error:
            print(colors.red(f'H.read: Unable to read "{fn}"'))
        if __debug__:
            print(f"H.read({prefix}, {frame_number})", subband.shape, subband.dtype, os.path.getsize(fn))
        subband_int32 = np.array(subband, dtype=np.int32)
        subband_int32 -= 32768
        H.append(subband_int32)
    return tuple(H)

def write(H: tuple, prefix: str, frame_number: int) -> None:
    ASCII_frame_number = str(frame_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    sb = 0
    for sbn in subband_names:
        if __debug__:
            print(f"H.write({prefix}, {frame_number})", H[sb].shape, H[sb].dtype, end=' ')
        subband = np.array(H[sb], dtype=np.int32)
        #subband = H[sb]
        #subband = H[i].astype(np.float32)
        subband += 32768
        subband = subband.astype(np.uint16)
        subband = cv2.cvtColor(subband, cv2.COLOR_RGB2BGR)
        fn = f"{prefix}{sbn}{ASCII_frame_number}.png"
        cv2.imwrite(fn, subband)
        sb += 1
        if __debug__:
            print(os.path.getsize(fn))

def interpolate(H: tuple) -> np.ndarray:
    LL = np.zeros(shape=(H[0].shape), dtype=np.float64)
    _H_ = DWT.synthesize_step(LL, H)
    return _H_

def reduce(_H_: np.ndarray) -> tuple:
    _, H = DWT.analyze_step(_H_)
    return H
