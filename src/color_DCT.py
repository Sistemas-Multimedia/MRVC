# Deprecated: use ~/repos/color-DCT/color-DCT.py

''' MRVC/color-DCT.py '''

import numpy as np
from scipy.fftpack import dct, idct

DCT_type = 3
norm = "ortho" # Orthonormal: orthogonal + unitary (unit gain in both directions of the transform)
#norm = None

name = "color-DCT"

def from_RGB(RGB_img: np.ndarray) -> np.ndarray:
    DCT_img = np.empty_like(RGB_img).astype(np.float)
    for y in range(RGB_img.shape[0]):
        for x in range(RGB_img.shape[1]):
            DCT_img[y, x] = dct(RGB_img[y, x], type=DCT_type, norm=norm)
    return DCT_img

def to_RGB(DCT_img: np.ndarray) -> np.ndarray:
    RGB_img = np.empty_like(DCT_img)
    for y in range(DCT_img.shape[0]):
        for x in range(DCT_img.shape[1]):
            RGB_img[y, x] = idct(DCT_img[y, x], type=DCT_type, norm=norm)
    return RGB_img
