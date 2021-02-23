''' MRVC/DWT.py '''

import numpy as np
import pywt

#WAVELET = pywt.Wavelet("haar")
WAVELET = pywt.Wavelet("db5")
#WAVELET = pywt.Wavelet("bior3.5")
N_LEVELS = 3

def analyze_step(color_frame: np.ndarray, wavelet: pywt.Wavelet =WAVELET) -> list:
    n_channels = color_frame.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.dwt2(data=color_frame[:,:,c], wavelet=wavelet, mode='per')
    return color_decomposition

def synthesize_step(color_decomposition: list, wavelet: pywt.Wavelet =WAVELET) -> np.ndarray:
    n_channels = len(color_decomposition)
    color_frame = []
    for c in range(n_channels):
        channel = pywt.idwt2(color_decomposition[c], wavelet=wavelet, mode='per')
        color_frame.append(channel)
    return np.array(color_frame)

def analyze(color_frame: np.ndarray, wavelet: pywt.Wavelet =WAVELET, n_levels: int =N_LEVELS) -> list:
    n_channels = color_frame.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.wavedec2(data=color_frame[:,:,c], wavelet=wavelet, mode='per', level=n_levels)
    return color_decomposition # A list of "gray" decompositions

def synthesize(color_decomposition: list, wavelet: pywt.Wavelet =WAVELET) -> ndarray:
    n_channels = len(color_decomposition)
    _color_frame = []
    for c in range(n_channels):
        channel = pywt.waverec2(color_decomposition[c], wavelet=wavelet, mode='per')
        _color_frame.append(channel)
    n_rows = _color_frame[0].shape[0]
    n_columns = _color_frame[0].shape[1]
    color_frame = np.ndarray((n_rows, n_columns, n_channels), np.float64)
    for c in range(n_channels):
        color_frame[:,:,c] = _color_frame[c][:,:]
    return color_frame

def __analyze_step(color_frame, wavelet=WAVELET):
    n_channels = color_frame.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.dwt2(data=color_frame[:,:,c], wavelet=wavelet, mode='per')
    n_rows_subband, n_columns_subband = color_decomposition[0][0].shape
    LL = np.empty(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    LH = np.empty(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    HL = np.empty(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    HH = np.empty(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    for c in range(n_channels):
        LL[:,:,c] = color_decomposition[c][0][:,:]
        LH[:,:,c] = color_decomposition[c][1][0][:,:]
        HL[:,:,c] = color_decomposition[c][1][1][:,:]
        HH[:,:,c] = color_decomposition[c][1][2][:,:]
    return (LL, (LH, HL, HH))

def __synthesize_step(LL, H, wavelet=WAVELET):
    LH, HL, HH = H
    n_channels = LL.shape[2] #len(LL)
    _color_frame = []
    for c in range(n_channels):
        frame = pywt.idwt2((LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), wavelet=wavelet, mode='per')
        #frame = pywt.idwt2((LL[:,:,c], np.array(H)[:,:,c]), wavelet=wavelet, mode='per')
        _color_frame.append(frame)
    n_rows, n_columns = _color_frame[0].shape
    #n_rows = _color_frame[0].shape[0]
    #n_columns = _color_frame[0].shape[1]
    color_frame = np.ndarray((n_rows, n_columns, n_channels), dtype=np.float64)
    for c in range(n_channels):
        color_frame[:,:,c] = _color_frame[c][:,:]
    return color_frame

def __analyze(color_frame, wavelet=WAVELET, levels=N_LEVELS):
    H = [None]*levels
    L, H[0] = analyze_step(color_frame, wavelet)
    for i in range(levels-1):
        L, H[i+1] = analyze_step(L, wavelet)
    #return [L, *H[::-1]]
    return [L, *H]

def __synthesize(color_decomposition, wavelet=WAVELET, n_levels=N_LEVELS):
    color_frame = synthesize_step(color_decomposition[0], color_decomposition[1], wavelet)
    for i in range(n_levels-1):
        color_frame = synthesize_step(color_frame, color_decomposition[i], wavelet)
    return color_frame

