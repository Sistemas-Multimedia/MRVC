''' MRVC/DWT.py '''

import numpy as np
import pywt
#import config
#import distortion
import frame
import L_DWT as L
import H_DWT as H

#WAVELET = pywt.Wavelet("haar")
WAVELET = pywt.Wavelet("db5")
#WAVELET = pywt.Wavelet("bior3.5")

# Number of levels of the DWT
#N_LEVELS = config.n_levels
N_LEVELS = 5

# Signal extension mode
#EXTENSION_MODE = "symmetric" # default
#EXTENSION_MODE = "constant"
#EXTENSION_MODE = "reflect"
#EXTENSION_MODE = "periodic"
#EXTENSION_MODE = "smooth"
#EXTENSION_MODE = "antisymmetric"
#EXTENSION_MODE = "antireflect"
EXTENSION_MODE = "periodization" # Gets the inimal number of coeffs
#EXTENSION_MODE = config.dwt_extension_mode

print("Wavelet =", WAVELET)
print("DWT extension mode =", EXTENSION_MODE)

def analyze_step(color_frame: np.ndarray) -> tuple:
    n_channels = color_frame.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.dwt2(data=color_frame[:,:,c], wavelet=WAVELET, mode=EXTENSION_MODE)
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

def synthesize_step(LL: np.ndarray, H: tuple) -> np.ndarray:
    LH, HL, HH = H
    n_channels = LL.shape[2] #len(LL)
    _color_frame = []
    for c in range(n_channels):
        frame = pywt.idwt2((LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), wavelet=WAVELET, mode=EXTENSION_MODE)
        #frame = pywt.idwt2((LL[:,:,c], np.array(H)[:,:,c]), wavelet=wavelet, mode=EXTENSION_MODE)
        _color_frame.append(frame)
    n_rows, n_columns = _color_frame[0].shape
    #n_rows = _color_frame[0].shape[0]
    #n_columns = _color_frame[0].shape[1]
    color_frame = np.ndarray((n_rows, n_columns, n_channels), dtype=np.float64)
    for c in range(n_channels):
        color_frame[:,:,c] = _color_frame[c][:,:]
    return color_frame

def analyze(color_frame: np.ndarray, n_levels: int =N_LEVELS) -> list:
    n_channels = color_frame.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.wavedec2(data=color_frame[:,:,c], wavelet=WAVELET, mode=EXTENSION_MODE, level=n_levels)

    output = []
    # LL^n_levels and H^n_levels subbands (both have the same resolution)
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
    
    # For the rest of SRLs (have increasing resolutions)
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

    return output # [LL^n, (LH^n, HL^n, HH^n), ..., (LH^1, HL^1, HH^1)], each subband panchromatic.

# No está terminado. Hay que crear las matrices en color a partir de las matrices monocromo.
def synthesize(color_decomposition: list, n_levels: int =None) -> np.ndarray:
    _color_frame = []
    n_channels = color_decomposition[0].shape[2]
    for c in range(n_channels):
        decomposition = [color_decomposition[0][:,:,c]] # LL^n
        for l in range(1, n_levels+1):
            decomposition.append((color_decomposition[l][0][:,:,c], color_decomposition[l][1][:,:,c], color_decomposition[l][2][:,:,c])) # (LH^l, HL^l, HH^l)
        _color_frame.append(pywt.waverec2(decomposition, wavelet=WAVELET, mode=EXTENSION_MODE))
    color_frame = np.ndarray((_color_frame[0].shape[0], _color_frame[0].shape[1], n_channels), dtype=_color_frame[0].dtype)
    print(_color_frame[0].shape, color_frame.shape)
    for c in range(n_channels):
        color_frame[:,:,c] = _color_frame[c][:,:]
    
    #print(n_channels)
    #_color_frame = []
    #for c in range(n_channels):
    #    channel = pywt.waverec2(color_decomposition[c], wavelet=WAVELET, mode=EXTENSION_MODE)
    #    _color_frame.append(channel)
    #n_rows = _color_frame[0].shape[0]
    #n_columns = _color_frame[0].shape[1]
    #color_frame = np.ndarray((n_rows, n_columns, n_channels), np.float64)
    #for c in range(n_channels):
    #    color_frame[:,:,c] = _color_frame[c][:,:]
    return color_frame

def compute_gains(n_levels):
    gains = [1.0]*n_levels
    for l in range(1,n_levels):
        gains[l] = gains[l-1]*1
    return gains

# Write each subband of a decomposition in a different PNG file using
# <prefix><frame_number><LL|LH|HL|HH><level>.png filename.
def write(color_decomposition:list, prefix:str, frame_number:int) -> None:
    n_channels = color_decomposition[0].shape[2]
    #_color_frame = [None]*n_channels
    n_resolutions = len(color_decomposition)
    LL = color_decomposition[0]
    L.write(LL, f"{prefix}{n_resolutions-1}", frame_number)
    resolution_index = n_resolutions-1
    for resolution in color_decomposition[1:]:
        H.write(resolution, f"{prefix}{resolution_index}", frame_number)
        resolution_index -= 1
        
    #for c in range(n_channels):
    #    decomposition = [color_decomposition[0][:,:,c]]
    #    LL = decomposition[0]
    #    for l in range(1, n_levels+1):
    #        decomp.append((color_decomp[l][0][:,:,c], color_decomp[l][1][:,:,c], color_decomp[l][2][:,:,c]))
    #    _color_frame[c], slices = pywt.coeffs_to_array(decomp)
    #color_frame = np.ndarray((_color_frame[0].shape[0], _color_frame[0].shape[1], n_channels), dtype=_color_frame[0].dtype)
    #for c in range(n_channels):
    #    color_frame[:,:,c] = _color_frame[c][:,:]
    #frame.write(color_frame.astype(np.int16), fn)
    #return slices

#def read(prefix:str, slices:list=None) -> np.ndarray: 
def read(prefix:str, frame_number:int) -> np.ndarray: 
    color_frame = frame.read(fn)
    n_channels = color_frame.shape[2]
    color_decomp = [None]*n_channels
    for c in range(n_channels):
        color_decomp[c] = pywt.array_to_coeffs(color_frame[:,:,c], slices, output_format='wavedec2')
    output = []
    n_rows_subband, n_columns_subband = color_decomposition[0][0].shape
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
    for r in range(2, n_levels+1):
        n_rows_subband, n_columns_subband = color_decomposition[0][r][0].shape
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
    
################

def __compute_deltas(n_levels):
    delta = []
    dims = (512, 512, 3)
    x = np.zeros(dims)
    L = DWT.analyze(x, n_levels)
    L[0][1,1,:] = [100, 100, 100]
    y = DWT.synthesize(L, l)
    e = distortion.average_energy(y)
    for l in range(1, n_levels):
        x = np.zeros(dims)
        L = LP.analyze(x, n_levels)
        L[l][1,1,:] = [100, 100, 100]
        y = DWT.synthesize(L)
        ee = distortion.average_energy(y)
        gain = e/ee
        delta.append(gain)
        print(gain)
        e = ee
    return delta

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

