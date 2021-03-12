''' MRVC/distortion.py '''

import numpy as np
import frame

def average_energy(x):
    return np.sum(x.astype(np.double)*x.astype(np.double))/(np.size(x))

def MSE(x, y):
    error_signal = x.astype(np.float32) - y
    return average_energy(error_signal)

def RMSE(x, y):
    error_signal = xx.astype(np.float32) - y
    return math.sqrt(MSE(error_signal))

def AMSE(x_prefix, y_prefix, n_frames):
    total_AMSE = 0
    for k in range(n_frames):
        x = frame.read(x_prefix, k)
        y = frame.read(y_prefix, k)
        _AMSE = MSE(x, y)
        print(f"AMSE of frame {k} = {AMSE}")
        total_AMSE += _AMSE
    _AMSE = total_AMSE/n_frames
    print("Average Mean Square Error (entire sequence)=", _AMSE)
    return _AMSE
