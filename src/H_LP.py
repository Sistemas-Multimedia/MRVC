''' MRVC/H.py '''

import numpy as np
import LP
import cv2 as cv
import colored
if __debug__:
    import os
    import frame

def read(prefix: str, frame_number: int, shape: tuple) -> np.ndarray:
    if __debug__:
        print(colored.fore.GREEN + f"H.read({prefix}, {frame_number})", end=' ')
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}{ASCII_frame_number}H.png"
    subband = cv.imread(fn, cv.IMREAD_UNCHANGED)
    try:
        subband = cv.cvtColor(subband, cv.COLOR_BGR2RGB)
    except cv.error:
        print(colored.fore.RED + f'H.read: Unable to read "{fn}"')
    if __debug__:
        print(f"{subband.shape} {subband.dtype} {os.path.getsize(fn)}", colored.style.RESET)
    subband_int32 = np.array(subband, dtype=np.int32)
    subband_int32 -= 32768
    return subband_int32

def write(H: np.ndarray, prefix: str, frame_number: int) -> None:
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}{ASCII_frame_number}H.png"
    if __debug__:
        print(colored.fore.GREEN + f"H.write({fn})", H.shape, H.max(), H.min(), H.dtype, end=' ')
    subband = np.array(H, dtype=np.int32)
    subband += 32768
    assert (subband < 65536).all()
    assert (subband > -1).all()
    subband = subband.astype(np.uint16)
    subband = cv.cvtColor(subband, cv.COLOR_RGB2BGR)
    cv.imwrite(fn, subband)
    if __debug__:
        print(colored.fore.GREEN + f"{os.path.getsize(fn)}", colored.style.RESET)

def interpolate(H: np.ndarray) -> np.ndarray:
    return H.astype(np.float64)

def reduce(_H_: np.ndarray) -> np.ndarray:
    return _H_
