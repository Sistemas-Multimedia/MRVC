''' MRVC/deadzone_quantizer.py '''

import numpy as np

# Quantization step.
#step = 0.5
#step = 1
#step = 8
#step = 16
#step = 54
#step = 128

#print("Quantization step =", step)

name = "dead-zone"

def quantize(x: np.ndarray, step: float) -> np.ndarray:
    assert step > 0
    k = (x / step).astype(np.int16) # Quantization indexes
    #k = (x / step).astype(np.int32)
    #return k.astype(np.float32)
    return k

def dequantize(k: np.ndarray, step: float) -> np.ndarray:
    y = step * k
    return y

def quan_dequan(x: np.ndarray, step:float) -> np.ndarray:
    k = quantize(x, step)
    y = dequantize(k, step)
    return y, k
