''' MRVC/QDWT_codec.py '''

import Q
import DWT
import numpy as np

N_LEVELS = 5

def encode(fn:str, frame: np.ndarray, step: float=step, n_levels:int =N_LEVELS) -> None:
    decomposition = DWT.analyze(frame, n_levels=n_levels)
    cAn = decomposition[0]
    quantized_cAn = Q.quantize(cAn, step)
    L.write(quantized_cAn, fn+"LL")
    rest_of_resolutions = decomposition[1:]
    for resolution in rest_of_resolutions:
        quantized_resolution = []
        for subband in resolution:
            quantized_subband = Q.quantize(subband, step)
            quantized_resolution.append(quantized_subband)
        H.write(quantized_subband, fn+"LH") 

def decode(fn:str, step:float=step, n_levels:int=N_LEVELS) -> np.array:
    dequantized_decomposition = []
    cAn = L.read(fn+"LL")
    dequantized_cAn = Q.dequantize(cAn, step)
    dequantized_decomposition.append(dequantized_cAn)
    for resolution_index in range(n_levels):
        dequantized_resolution = []
        resolution = H.read(fn)
        for subband in resolution:
            dequantized_subband = Q.dequantize(subband, step)
            dequantized_resolution.append(dequantized_subband)
        dequantized_decomposition.append(tuple(dequantized_resolution))
    reconstructed_frame = DWT.synthesize(dequantized_decomposition)
    return reconstructed_frame
