''' MRVC/LP.py '''

import numpy as np
import cv2 as cv
import config

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
