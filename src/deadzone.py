''' MRVC/deadzone.py '''

import numpy as np

Q_STEP = 1

def quantize(x, q_step=Q_STEP):
    k = (x / q_step).astype(np.int16)
    return k

def dequantize(k, q_step=Q_STEP):
    y = q_step * k
    return y
