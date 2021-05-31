''' MRVC/DWT.py

Provides:

1. Multichannel 1-level DWT and inverse DWT.
2. Multichannel N-levels DWT and inverser DWT.
3. Subband gains computation.
3. Decomposition I/O.

'''

import numpy as np
import pywt
#import config
#import distortion
import image
import L_DWT as L
import H_DWT as H

_wavelet = pywt.Wavelet("haar")
#wavelet = pywt.Wavelet("db1")
#wavelet = pywt.Wavelet("db5")
#wavelet = pywt.Wavelet("db20")
#wavelet = pywt.Wavelet("bior3.5")
#wavelet = pywt.Wavelet("bior3.7")
#wavelet = pywt.Wavelet("bior6.8")
#wavelet = pywt.Wavelet("rbio6.8")

# Number of levels of the DWT
#N_levels = config.n_levels
_N_levels = 5

# Signal extension mode
#_extension_mode = "symmetric" # default
#_extension_mode = "constant"
#_extension_mode = "reflect"
#_extension_mode = "periodic"
#_extension_mode = "smooth"
#_extension_mode = "antisymmetric"
#_extension_mode = "antireflect"
_extension_mode = "periodization" # Generates the inimal number of coeffs
#_extension_mode = config.dwt_extension_mode

print("Wavelet =", _wavelet)
print("DWT extension mode =", _extension_mode)

def analyze_step(color_image:np.ndarray, wavelet:pywt.Wavelet=_wavelet) -> tuple:
    n_channels = color_image.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.dwt2(data=color_image[:,:,c], wavelet=wavelet, mode=_extension_mode)
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

def synthesize_step(LL:np.ndarray, H:tuple, wavelet:pywt.Wavelet=_wavelet) -> np.ndarray:
    LH, HL, HH = H
    n_channels = LL.shape[2] #len(LL)
    _color_image = []
    for c in range(n_channels):
        image = pywt.idwt2((LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), wavelet=wavelet, mode=_extension_mode)
        #image = pywt.idwt2((LL[:,:,c], np.array(H)[:,:,c]), wavelet=wavelet, mode=_extension_mode)
        _color_image.append(image)
    n_rows, n_columns = _color_image[0].shape
    #n_rows = _color_image[0].shape[0]
    #n_columns = _color_image[0].shape[1]
    color_image = np.ndarray((n_rows, n_columns, n_channels), dtype=np.float64)
    for c in range(n_channels):
        color_image[:,:,c] = _color_image[c][:,:]
    return color_image

def analyze(color_image:np.ndarray, wavelet:pywt.Wavelet=_wavelet, N_levels:int=_N_levels) -> list:
    n_channels = color_image.shape[2]
    color_decomposition = [None]*n_channels
    for c in range(n_channels):
        color_decomposition[c] = pywt.wavedec2(data=color_image[:,:,c], wavelet=wavelet, mode=_extension_mode, level=N_levels)

    output = []
    # LL^N_levels and H^N_levels subbands (both have the same resolution)
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
    for r in range(2, N_levels+1):
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

def synthesize(color_decomposition:list, wavelet:pywt.Wavelet=_wavelet, N_levels:int=_N_levels) -> np.ndarray:
    _color_image = []
    n_channels = color_decomposition[0].shape[2]
    for c in range(n_channels):
        decomposition = [color_decomposition[0][:,:,c]] # LL^n
        for l in range(1, N_levels+1):
            decomposition.append((color_decomposition[l][0][:,:,c], color_decomposition[l][1][:,:,c], color_decomposition[l][2][:,:,c])) # (LH^l, HL^l, HH^l)
        _color_image.append(pywt.waverec2(decomposition, wavelet=wavelet, mode=_extension_mode))
    color_image = np.ndarray((_color_image[0].shape[0], _color_image[0].shape[1], n_channels), dtype=_color_image[0].dtype)
    #print(_color_image[0].shape, color_image.shape)
    for c in range(n_channels):
        color_image[:,:,c] = _color_image[c][:,:]
    
    #print(n_channels)
    #_color_image = []
    #for c in range(n_channels):
    #    channel = pywt.waverec2(color_decomposition[c], wavelet=wavelet, mode=_extension_mode)
    #    _color_image.append(channel)
    #n_rows = _color_image[0].shape[0]
    #n_columns = _color_image[0].shape[1]
    #color_image = np.ndarray((n_rows, n_columns, n_channels), np.float64)
    #for c in range(n_channels):
    #    color_image[:,:,c] = _color_image[c][:,:]
    return color_image

# Ojo, que esto no está terminado!!!!!!!!!!!!!!!!!!!!!!
def compute_gains(N_levels):
    gains = [1.0]*N_levels
    for l in range(1,N_levels):
        gains[l] = gains[l-1]*2
    return gains

# Write each subband of a decomposition in a different PNG file using
# <prefix><image_number><LL|LH|HL|HH><level>.png filename.
def write(color_decomposition:list, prefix:str, image_number:int=0, N_levels:int=_N_levels) -> None:
    n_channels = color_decomposition[0].shape[2]
    #_color_image = [None]*n_channels
    #n_resolutions = len(color_decomposition)
    #n_resolutions = N_levels+1
    LL = color_decomposition[0]
    L.write(LL, f"{prefix}_{N_levels}", image_number)
    resolution_index = N_levels
    for resolution in color_decomposition[1:]:
        H.write(resolution, f"{prefix}_{resolution_index}", image_number)
        resolution_index -= 1
        
    #for c in range(n_channels):
    #    decomposition = [color_decomposition[0][:,:,c]]
    #    LL = decomposition[0]
    #    for l in range(1, n_levels+1):
    #        decomp.append((color_decomp[l][0][:,:,c], color_decomp[l][1][:,:,c], color_decomp[l][2][:,:,c]))
    #    _color_image[c], slices = pywt.coeffs_to_array(decomp)
    #color_image = np.ndarray((_color_image[0].shape[0], _color_image[0].shape[1], n_channels), dtype=_color_image[0].dtype)
    #for c in range(n_channels):
    #    color_image[:,:,c] = _color_image[c][:,:]
    #image.write(color_image.astype(np.int16), fn)
    #return slices

#def read(prefix:str, slices:list=None) -> np.ndarray: 
def read(prefix:str, image_number:int=0, N_levels:int=_N_levels) -> np.ndarray:
    LL = L.read(f"{prefix}_{N_levels+1}", image_number)
    color_decomposition = [LL]
    shape = list(LL.shape)
    for l in range(N_levels+1, 0, -1):
        resolution = H.read(f"{prefix}_{l}", image_number, tuple(shape))
        color_decomposition.append(resolution)
        shape[0] *= 2
        shape[1] *= 2
    return color_decomposition
    #color_image = image.read(f)
    #n_channels = color_image.shape[2]
    #color_decomp = [None]*n_channels
    #for c in range(n_channels):
    #    color_decomp[c] = pywt.array_to_coeffs(color_image[:,:,c], slices, output_format='wavedec2')
    #output = []
    #n_rows_subband, n_columns_subband = color_decomposition[0][0].shape
    #LL = np.empty(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    #LH = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    #HL = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    #HH = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    #for c in range(n_channels): # For each color component
    #    LL[:,:,c] = color_decomposition[c][0][:,:]
    #    LH[:,:,c] = color_decomposition[c][1][0][:,:]
    #    HL[:,:,c] = color_decomposition[c][1][1][:,:]
    #    HH[:,:,c] = color_decomposition[c][1][2][:,:]
    #output.append(LL)
    #output.append((LH, HL, HH))
    #for r in range(2, n_levels+1):
    #    n_rows_subband, n_columns_subband = color_decomposition[0][r][0].shape
    #    prev_n_columns_subband = n_columns_subband
    #    LH = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    #    HL = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    #    HH = np.zeros(shape=(n_rows_subband, n_columns_subband, n_channels), dtype=np.float64)
    #    for c in range(n_channels):
    #        LH[:,:,c] = color_decomposition[c][r][0][:,:]
    #        HL[:,:,c] = color_decomposition[c][r][1][:,:]
    #        HH[:,:,c] = color_decomposition[c][r][2][:,:]
    #    output.append((LH, HL, HH))

    #return output

'''
def normalize_256(color_decomposition:list, n_levels:int) -> (list, float, float):
    #Normalize the decomposition to the range [0, 255]. The maximum n
and the minimum values are also returned.
    n_channels = color_decomposition[0].shape[2]
    #_color_image = [None]*n_channels
    #n_resolutions = len(color_decomposition)
    #n_resolutions = n_levels+1
    max = -100000
    min = 100000
    LL = color_decomposition[0]
    max = 
    L.write(LL, f"{prefix}_{n_levels}", image_number)
    resolution_index = n_levels
    for resolution in color_decomposition[1:]:
        H.write(resolution, f"{prefix}_{resolution_index}", image_number)
        resolution_index -= 1
'''
    
    
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

def __analyze_step(color_image, wavelet=_wavelet):
    n_rows, n_columns, n_channels = color_image.shape[0]//2, color_image.shape[1]//2, color_image.shape[2]
    LL = np.empty(shape=(n_rows, n_columns, n_channels), dtype=np.float64)
    LH = np.empty(shape=(n_rows, n_columns, n_channels), dtype=np.float64)
    HL = np.empty(shape=(n_rows, n_columns, n_channels), dtype=np.float64)
    HH = np.empty(shape=(n_rows, n_columns, n_channels), dtype=np.float64)
    #n_channels = color_image.shape[2]
    #color_decomposition = [None]*n_channels
    for c in range(n_channels):
        #color_decomposition[c] = pywt.dwt2(data=color_image[:,:,c], wavelet=wavelet, mode='per')
        LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c]) = pywt.dwt2(data=color_image[:,:,c], wavelet=wavelet, mode='per')
    #return color_decomposition
    #return np.array([color_decomposition[0][0], color_decomposition[1][0], color_decomposition[2][0]]), ()
    return (LL, (LH, HL, HH))

def __synthesize_step(LL, H, wavelet=_wavelet):
    n_channels = len(color_decomposition)
    color_image = []
    for c in range(n_channels):
        channel = pywt.idwt2(color_decomposition[c], wavelet=wavelet, mode='per')
        color_image.append(channel)
    return np.array(color_image)
def __analyze(color_image, wavelet=_wavelet, levels=_N_levels):
    H = [None]*levels
    L, H[0] = analyze_step(color_image, wavelet)
    for i in range(levels-1):
        L, H[i+1] = analyze_step(L, wavelet)
    #return [L, *H[::-1]]
    return [L, *H]

def __synthesize(color_decomposition, wavelet=_wavelet, N_levels=_N_levels):
    color_image = synthesize_step(color_decomposition[0], color_decomposition[1], wavelet)
    for i in range(N_levels-1):
        color_image = synthesize_step(color_image, color_decomposition[i], wavelet)
    return color_image
