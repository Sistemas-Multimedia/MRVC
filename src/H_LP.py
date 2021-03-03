''' MRVC/H.py '''

import numpy as np
import LP
import cv2 as cv
import colors
if __debug__:
    import os
    import frame

def read(prefix: str, frame_number: int, shape: tuple) -> np.ndarray:
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}H{ASCII_frame_number}.png"
    subband = cv.imread(fn, cv.IMREAD_UNCHANGED)
    try:
        subband = cv.cvtColor(subband, cv.COLOR_BGR2RGB)
    except cv.error:
        print(colors.red(f'H.read: Unable to read "{fn}"'))
    if __debug__:
        print(f"H.read({prefix}, {frame_number})", subband.shape, subband.dtype, os.path.getsize(fn))
    subband_int32 = np.array(subband, dtype=np.int32)
    subband_int32 -= 32768
    return subband_int32

def write(H: np.ndarray, prefix: str, frame_number: int) -> None:
    ASCII_frame_number = str(frame_number).zfill(3)
    if __debug__:
        print(f"H.write({prefix}, {frame_number})", H.shape, H.max(), H.min(), H.dtype, end=' ')
    subband = np.array(H, dtype=np.int32)
    subband += 32768
    assert (subband < 65536).all()
    assert (subband > -1).all()
    subband = subband.astype(np.uint16)
    subband = cv.cvtColor(subband, cv.COLOR_RGB2BGR)
    fn = f"{prefix}H{ASCII_frame_number}.png"
    cv.imwrite(fn, subband)
    if __debug__:
        print(os.path.getsize(fn))

def interpolate(H: np.ndarray) -> np.ndarray:
    return H.astype(np.float64)

def reduce(_H_: np.ndarray) -> np.ndarray:
    return _H_
