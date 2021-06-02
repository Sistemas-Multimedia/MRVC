''' MRVC/distortion.py '''

import numpy as np
import image

def energy(x):
    return np.sum(x.astype(np.double)*x.astype(np.double))

def average_energy(x):
    return energy(x)/np.size(x)

def MSE(x, y):
    error_signal = x.astype(np.float64) - y
    return average_energy(error_signal)

def RMSE(x, y):
    error_signal = xx.astype(np.float64) - y
    return math.sqrt(MSE(error_signal))

def AMSE(x_prefix, y_prefix, n_images):
    print(f"AMSE: comparing {x_prefix} and {y_prefix}")
    total_AMSE = 0
    for k in range(n_images):
        x = image.read(x_prefix, k)
        y = image.read(y_prefix, k)
        _AMSE = MSE(x, y)
        print(f"AMSE of image {k} = {_AMSE}")
        total_AMSE += _AMSE
    _AMSE = total_AMSE/n_images
    print("Average Mean Square Error (entire sequence) =", _AMSE)
    return _AMSE
