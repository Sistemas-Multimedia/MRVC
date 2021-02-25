''' MRVC/deadzone.py '''

import numpy as np

Q_STEP = 1

def quantize(x: np.ndarray, q_step: float=Q_STEP) -> np.ndarray:
    k = (x / q_step).astype(np.int16)
    return k

def dequantize(k: np.ndarray, q_step: float=Q_STEP) -> np.ndarray:
    y = q_step * k
    return y
