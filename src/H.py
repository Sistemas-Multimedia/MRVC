''' MRVC/hybrid.py '''

import numpy as np
import DWT
import cv2

def read(prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    H = []
    sb = 0
    for sbn in subband_names:
        fn = f"{prefix}{sbn}{ASCII_frame_number}.png"
        subband = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
        subband = cv2.cvtColor(subband, cv2.COLOR_BGR2RGB)
        subband = np.array(subband, dtype=np.float64)
        subband -= 32768.0
        H.append(subband)
    return H # [LH, HL, HH], each one [rows, columns, components]

def write(H, prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    sb = 0
    for sbn in subband_names:
        subband = np.array(H[sb], dtype=np.float64)
        #subband = H[i].astype(np.float32)
        subband += 32768.0
        subband = subband.astype(np.uint16)
        fn = f"{prefix}{sbn}{ASCII_frame_number}.png"
        print(subband.shape, fn)
        subband = cv2.cvtColor(subband, cv2.COLOR_RGB2BGR)
        cv2.imwrite(fn, subband)
        sb += 1

def interpolate(H):
    LL = np.zeros(shape=(H[0].shape), dtype=np.float64)
    _H_ = DWT.synthesize(LL, H)
    return _H_

def reduce(_H_):
    _, H = DWT.analyze(_H_)
    return H
