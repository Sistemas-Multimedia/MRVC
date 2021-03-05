''' MRVC/MSE.py '''

import numpy as np

def average_energy(x):
    return np.sum(x.astype(np.double)*x.astype(np.double))/(np.size(x))

def MSE(x, y):
    error_signal = x.astype(np.float32) - y
    return average_energy(error_signal)

def RMSE(x, y):
    error_signal = xx.astype(np.float32) - y
    return math.sqrt(MSE(error_signal))
