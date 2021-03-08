''' MRVC/deadzone.py '''

import numpy as np

# Quantization step.
#step = 0.5
#step = 1
#step = 8
#step = 16
step = 54
#step = 128

print("Quantization step =", step)

def quantize(x: np.ndarray, step: float=step) -> np.ndarray:
    k = (x / step).astype(np.int16)
    #k = (x / step).astype(np.int32)
    #return k.astype(np.float32)
    return k

def dequantize(k: np.ndarray, step: float=step) -> np.ndarray:
    y = step * k
    return y
