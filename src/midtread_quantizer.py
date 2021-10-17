''' MRVC/mid-tread_quantizer.py '''

import numpy as np

name = "mid-tread"

def quantize(x: np.ndarray, step: float) -> np.ndarray:
    assert step > 0
    k = np.rint(x / step).astype(np.int)  # Quantization indexes
    #k = np.floor(x / step + 0.5).astype(np.int)  # Quantization indexes
    return k

def dequantize(k: np.ndarray, step: float) -> np.ndarray:
    y = step * k
    return y

def quan_dequan(x: np.ndarray, step:float, dtype=np.uint8) -> np.ndarray:
    k = quantize(x, step).astype(dtype)
    y = dequantize(k, step)
    return y, k
