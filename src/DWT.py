''' MRVC/DWT.py '''

import numpy as np
import pywt

WAVELET = pywt.Wavelet("db5")
#WAVELET = pywt.Wavelet("bior3.5")
N_LEVELS = 1

def analyze(color_frame, wavelet=WAVELET, n_levels=N_LEVELS):
    n_channels = color_frame.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.wavedec2(data=color_frame[:,:,c], wavelet=wavelet, mode='per', level=n_levels)
    #L = []
    #H = []
    #for c in range(n_channels):
    #    L.append(color_decomposition[c][0])
    #    H.append(color_decomposition[c][1])
    #return L, H
    return color_decomposition

#def synthesize(L, H, wavelet=WAVELET):
def synthesize(color_decomposition, wavelet=WAVELET):
    n_channels = len(L)
    _color_frame = []
    for c in range(n_channels):
        frame = pywt.waverec2([L[c], H[c]], wavelet=wavelet, mode='per')
        _color_frame.append(frame)
    n_rows = _color_frame[0].shape[0]
    n_columns = _color_frame[0].shape[1]
    color_frame = np.ndarray((n_rows, n_columns, n_channels), np.float64)
    for c in range(n_channels):
        color_frame[:,:,c] = _color_frame[c][:,:]
    return color_frame
