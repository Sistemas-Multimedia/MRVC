import cv2
import numpy as np
import pywt
import math

def forward(image):
    '''2D DWT of a color image.

    Arguments
    ---------

        image : [:,:,:].

            A color frame.

    Returns
    -------

        (L,H) where L=[:,:,:] and H=(LH,HL,HH), where LH,HL,HH=[:,:,:].

            A color pyramid.

    '''

    y = math.ceil(image.shape[0]/2)
    x = math.ceil(image.shape[1]/2)
    LL = np.ndarray((y, x, 3), np.float64)
    LH = np.ndarray((y, x, 3), np.float64)
    HL = np.ndarray((y, x, 3), np.float64)
    HH = np.ndarray((y, x, 3), np.float64)
    for c in range(3):
        (LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])) = pywt.dwt2(image[:,:,c], 'db5', mode='per')

    return (LL, (LH, HL, HH))

def backward(L, H):
    '''2D 1-iteration inverse DWT of a color pyramid.

    Arguments
    ---------

        L : [:,:,:].

            Low-frequency color subband.

        H : (LH, HL, HH), where LH,HL,HH=[:,:,:].

            High-frequency color subbands.

    Returns
    -------

        [:,:,:].

            A color frame.

    '''

    LH = H[0]
    HL = H[1]
    HH = H[2]
    frame = np.ndarray((L.shape[0]*2, L.shape[1]*2, 3), np.float64)
    for c in range(3):
        frame[:,:,c] = pywt.idwt2((L[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), 'db5', mode='per')
    return frame
