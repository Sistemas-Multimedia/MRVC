# Designed for testing purposes, The result from MCOLP should the the
# same that MDWT, because MCOLP would substract zeros.

import numpy as np

def generate_prediction(AL, BL, CL, AH, CH):
    return np.zeros(AL.shape, np.float64)

