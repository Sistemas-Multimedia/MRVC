''' MRVC/DWT.py '''

import numpy as np
import pywt
import config

#WAVELET = pywt.Wavelet("haar")
WAVELET = pywt.Wavelet(config.wavelet)
#WAVELET = pywt.Wavelet("bior3.5")
N_LEVELS = 3
#MODE = "symmetric" # default
#MODE = "constant"
#MODE = "reflect"
#MODE = "periodic"
#MODE = "smooth"
#MODE = "antisymmetric"
#MODE = "antireflect"
#MODE = "periodization" # Gets the inimal number of coeffs
MODE = config.extension_mode

def analyze_step(color_frame: np.ndarray, wavelet: pywt.Wavelet =WAVELET) -> tuple:
    n_channels = color_frame.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.dwt2(data=color_frame[:,:,c], wavelet=wavelet, mode=MODE)
    assert color_decomposition[0][0].shape == color_decomposition[0][1][0].shape
    n_rows_subband, n_columns_subband = color_decomposition[0][0].shape # All subbands have the same shape
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

def synthesize_step(LL: np.ndarray, H: tuple, wavelet: pywt.Wavelet =WAVELET) -> np.ndarray:
    LH, HL, HH = H
    n_channels = LL.shape[2] #len(LL)
    _color_frame = []
    for c in range(n_channels):
        frame = pywt.idwt2((LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), wavelet=wavelet, mode=MODE)
        #frame = pywt.idwt2((LL[:,:,c], np.array(H)[:,:,c]), wavelet=wavelet, mode=MODE)
        _color_frame.append(frame)
    n_rows, n_columns = _color_frame[0].shape
    #n_rows = _color_frame[0].shape[0]
    #n_columns = _color_frame[0].shape[1]
    color_frame = np.ndarray((n_rows, n_columns, n_channels), dtype=np.float64)
    for c in range(n_channels):
        color_frame[:,:,c] = _color_frame[c][:,:]
    return color_frame

def analyze(color_frame: np.ndarray, wavelet: pywt.Wavelet =WAVELET, n_levels: int =N_LEVELS) -> list:
    n_channels = color_frame.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.wavedec2(data=color_frame[:,:,c], wavelet=wavelet, mode=MODE, level=n_levels)

    output = []
    # LL^n_levels and H^n_levels subbands
    n_rows_subband, n_columns_subband = color_decomposition[0][0].shape # All subbands in the SRL with the same shape
    #prev_n_rows_subband = n_rows_subband
    #prev_n_columns_subband = n_columns_subband
    LL = np.empty(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    LH = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    HL = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    HH = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    for c in range(n_channels): # For each color component
        LL[:,:,c] = color_decomposition[c][0][:,:]
        LH[:,:,c] = color_decomposition[c][1][0][:,:]
        HL[:,:,c] = color_decomposition[c][1][1][:,:]
        HH[:,:,c] = color_decomposition[c][1][2][:,:]
    output.append(LL)
    output.append((LH, HL, HH))
    
     # For the rest of SRLs
    for r in range(2, n_levels+1):
        n_rows_subband, n_columns_subband = color_decomposition[0][r][0].shape
        #if prev_n_rows_subband * 2 < n_rows_subband:
        #    n_rows_subband += 1
        #prev_n_rows_subband = n_rows_subband
        #if prev_n_columns_subband * 2 < n_columns_subband:
        #    n_columns_subband += 1
        prev_n_columns_subband = n_columns_subband
        LH = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
        HL = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
        HH = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
        for c in range(n_channels):
            LH[:,:,c] = color_decomposition[c][r][0][:,:]
            HL[:,:,c] = color_decomposition[c][r][1][:,:]
            HH[:,:,c] = color_decomposition[c][r][2][:,:]
        output.append((LH, HL, HH))

    return output

def synthesize(color_decomposition: list, wavelet: pywt.Wavelet =WAVELET) -> np.ndarray:
    n_channels = len(color_decomposition)
    _color_frame = []
    for c in range(n_channels):
        channel = pywt.waverec2(color_decomposition[c], wavelet=wavelet, mode=MODE)
        _color_frame.append(channel)
    n_rows = _color_frame[0].shape[0]
    n_columns = _color_frame[0].shape[1]
    color_frame = np.ndarray((n_rows, n_columns, n_channels), np.float64)
    for c in range(n_channels):
        color_frame[:,:,c] = _color_frame[c][:,:]
    return color_frame

################

def __analyze_step(color_frame, wavelet=WAVELET):
    n_rows, n_columns, n_channels = color_frame.shape[0]//2, color_frame.shape[1]//2, color_frame.shape[2]
    LL = np.empty(shape=(n_rows, n_columns, n_channels), dtype=np.float64)
    LH = np.empty(shape=(n_rows, n_columns, n_channels), dtype=np.float64)
    HL = np.empty(shape=(n_rows, n_columns, n_channels), dtype=np.float64)
    HH = np.empty(shape=(n_rows, n_columns, n_channels), dtype=np.float64)
    #n_channels = color_frame.shape[2]
    #color_decomposition = [None]*n_channels
    for c in range(n_channels):
        #color_decomposition[c] = pywt.dwt2(data=color_frame[:,:,c], wavelet=wavelet, mode='per')
        LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c]) = pywt.dwt2(data=color_frame[:,:,c], wavelet=wavelet, mode='per')
    #return color_decomposition
    #return np.array([color_decomposition[0][0], color_decomposition[1][0], color_decomposition[2][0]]), ()
    return (LL, (LH, HL, HH))

def __synthesize_step(LL, H, wavelet=WAVELET):
    n_channels = len(color_decomposition)
    color_frame = []
    for c in range(n_channels):
        channel = pywt.idwt2(color_decomposition[c], wavelet=wavelet, mode='per')
        color_frame.append(channel)
    return np.array(color_frame)
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

