''' MRVC/deadzone.py '''

import numpy as np

def quantize(x, quantization_step):
    k = (x / quantization_step).astype(np.int16)
    return k

def dequantize(k, quantization_step):
    y = quantization_step * k
    return y
