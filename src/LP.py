''' MRVC/LP.py '''

import numpy as np
import cv2 as cv
import config
import MSE

def analyze_step(frame: np.ndarray) -> tuple:
    L = cv.pyrDown(frame)
    interpolated_L = cv.pyrUp(L)
    _frame = np.zeros(interpolated_L.shape)
    #print(_frame.shape, interpolated_L.shape)
    _frame[:frame.shape[0], :frame.shape[1], :] = frame
    H = _frame - interpolated_L
    return (L, H)

def analyze(frame: np.ndarray, n_levels: int =config.n_levels) -> list:
    L, H = analyze_step(frame)
    P = [H]
    for l in range(n_levels-1):
        L, H = analyze_step(L)
        P.append(H)
    P.append(L)
    return P[::-1]

def synthesize_step(L: np.ndarray, H:np.ndarray) -> np.ndarray:
    interpolated_L = cv.pyrUp(L)
    _H = np.zeros(interpolated_L.shape)
    _H[:H.shape[0], :H.shape[1], :] = H
    frame = _H + interpolated_L
    return frame

def synthesize(P: list, n_levels: int =config.n_levels) -> np.ndarray:
    #frame = P[n_levels]
    frame = P[0]
    for l in range(n_levels):
        #frame = cv.pyrUp(frame)
        #frame += P[n_levels-l-1]
        #frame = synthesize_step((P[n_levels-l-1], frame))
        frame = synthesize_step(frame, P[l+1])
    return frame

def compute_gains(n_levels):
    gains = [1.0]*n_levels
    #dims = (8192, 8, 3)
    #x = np.zeros(dims, dtype=np.int16)
    #L = analyze(x, n_levels)
    #L[0][1, 1, :] = [100, 100, 100]
    #y = synthesize(L, n_levels)
    #e = MSE.average_energy(y)
    #for l in range(1, n_levels):
    #    x = np.zeros(dims)
    #    L = analyze(x, n_levels)
    #    L[l][0, 0, :] = [100, 100, 100]
    #    y = synthesize(L, n_levels)
    #    ee = MSE.average_energy(y)
    #    gain = e/ee
    #    gains.append(gain)
    #    e = ee
    #gains = [None]*len(_gains)
    for l in range(1,n_levels):
    #    gains[l] = gains[l-1]*gains[l]
        gains[l] = gains[l-1]*4
    return gains
