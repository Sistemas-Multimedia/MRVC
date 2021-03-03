''' MRVC/LP.py '''

import numpy as np
import cv2 as cv
import config

def analyze_step(frame: np.ndarray) -> tuple:
    L = cv.pyrDown(frame)
    interpolated_L = cv.pyrUp(L)
    H = frame - interpolated_L
    return (H, L)

def analyze(frame: np.ndarray, n_levels: int =config.n_levels) -> list:
    H, L = analyze_step(frame)
    P = [H]
    for l in range(n_levels-1):
        H, L = analyze_step(L)
        P.append(H)
    P.append(L)
    return P

def synthesize_step(HL: tuple) -> np.ndarray:
    interpolated_L = cv.pyrUp(HL[1])
    frame = HL[0] + interpolated_L
    return frame

def synthesize(P: list, n_levels: int =config.n_levels) -> np.ndarray:
    frame = P[n_levels]
    for l in range(n_levels):
        #frame = cv.pyrUp(frame)
        #frame += P[n_levels-l-1]
        frame = synthesize_step((P[n_levels-l-1], frame))
    return frame
