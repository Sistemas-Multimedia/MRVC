''' MRVC/L.py '''

import numpy as np
import DWT
import cv2
import colors

def read(prefix: str, frame_number:int) -> np.ndarray: # [row, column, component]
    #ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}LL{frame_number:03d}.png"
    #fn = name + ".png"
    L = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    try:
        L = cv2.cvtColor(L, cv2.COLOR_BGR2RGB)
    except cv2.error:
        print(colors.red(f'L.read: Unable to read "{fn}"'))
        raise
    #subband = np.array(subband, dtype=np.float64)
    L -= 32768
    if __debug__:
        print(f"L.read({prefix}, {frame_number})", L.shape, L.dtype)
    return L

def write(L: np.ndarray, prefix: str, frame_number: int) -> None:
    #subband = np.array(L, dtype=np.float64)
    L += 32768
    #subband += 32768.0
    #subband = subband.astype(np.uint16)
    #ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}LL{frame_number:03d}.png"
    #fn = name + ".png"
    if __debug__:
        print(f"L.write({prefix}, {frame_number})", L.shape, L.dtype)
    L = cv2.cvtColor(L, cv2.COLOR_RGB2BGR)
    cv2.imwrite(fn, L)

def interpolate(L: np.ndarray) -> np.ndarray:
    LH = np.zeros(shape=L.shape, dtype=np.float64)
    HL = np.zeros(shape=L.shape, dtype=np.float64)
    HH = np.zeros(shape=L.shape, dtype=np.float64)
    H = (LH, HL, HH)
    _L_ = DWT.synthesize_step((L, H))
    return _L_

def reduce(_L_: np.ndarray) -> np.ndarray:
    L, _ = DWT.analyze_step(_L_)
    return L
