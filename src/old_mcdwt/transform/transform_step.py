import cv2
import numpy as np
import pywt
import math

from mcdwt import image_io
from mcdwt import pyramid_io
from mcdwt import motion

def _2D_DWT(image):
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

def _2D_iDWT(L, H):
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


def forward(input = '../input/', output='/tmp/', n=5, l=2):
    '''A Motion Compensated Discrete Wavelet Transform.

    Compute the 1D-DWT along motion trajectories. The input video (as
    a sequence of images) must be stored in disk (<input> directory)
    and the output (as a sequence of DWT coefficients that are called
    pyramids) will be stored in disk (<output> directory). So, this
    MCDWT implementation does not transform the video on the fly.

    Arguments
    ---------

        input : str

            Path where the input images are. Example:
            "../input/image".

        output : str

            Path where the (transformed) pyramids will be. Example:
            "../output/pyramid".

         n : int

            Number of images to process.

         l : int

            Number of leves of the MCDWT (temporal scales). Controls
            the GOP size. Examples: `l`=0 -> GOP_size = 1, `l`=1 ->
            GOP_size = 2, `l`=2 -> GOP_size = 4. etc.

    Returns
    -------

        None.

    '''
    
    #import ipdb; ipdb.set_trace()
    ir = image_io.ImageReader()
    iw = image_io.ImageWritter()
    pw = pyramid_io.PyramidWritter()
    x = 2
    for j in range(l): # Number of temporal scales
        #import ipdb; ipdb.set_trace()
        A = ir.read(0, input)
        tmpA = _2D_DWT(A)
        L_y = tmpA[0].shape[0]
        L_x = tmpA[0].shape[1]
        pw.write(tmpA, 0, output)        
        zero_L = np.zeros(tmpA[0].shape, np.float64)
        zero_H = (zero_L, zero_L, zero_L)
        AL = _2D_iDWT(tmpA[0], zero_H)
        iw.write(AL, 1)
        AH = _2D_iDWT(zero_L, tmpA[1])
        iw.write(AH, 1)
        i = 0
        while i < (n//x):
            B = ir.read(x*i+x//2, input)
            tmpB = _2D_DWT(B)
            BL = _2D_iDWT(tmpB[0], zero_H)
            BH = _2D_iDWT(zero_L, tmpB[1])
            C = ir.read(x*i+x, input)
            tmpC = _2D_DWT(C)
            pw.write(tmpC, x*i+x, output)
            CL = _2D_iDWT(tmpC[0], zero_H)
            CH = _2D_iDWT(zero_L, tmpC[1])
            BHA = motion.motion_compensation(BL, AL, AH)
            BHC = motion.motion_compensation(BL, CL, CH)
            iw.write(BH, x*i+x//2, output+'predicted')
            prediction = (BHA + BHC) / 2
            try:
                iw.write(prediction+128, x*i+x//2, output+'prediction')
            except:
                pass
            rBH = BH - prediction
            try:
                iw.write(rBH, x*i+x//2, output+'residue')
            except:
                pass
            rBH = _2D_DWT(rBH)
            #import ipdb; ipdb.set_trace()
            try:
                pw.write(rBH, x*i+x//2 + 1000)
            except:
                pass
            rBH[0][0:L_y,0:L_x,:] = tmpB[0]
            try:
                pw.write(rBH, x*i+x//2, output)
            except:
                pass
            AL = CL
            AH = CH
            i += 1
            print('i =', i)
        x *= 2

def backward(input = '/tmp/', output='/tmp/', n=5, l=2):
    '''A (Inverse) Motion Compensated Discrete Wavelet Transform.

    iMCDWT is the inverse transform of MCDWT. Inputs a sequence of
    pyramids and outputs a sequence of images.

    Arguments
    ---------

        input : str

            Path where the input pyramids are. Example:
            "../input/image".

        output : str

            Path where the (inversely transformed) images will
            be. Example: "../output/pyramid".

         n : int

            Number of pyramids to process.

         l : int

            Number of leves of the MCDWT (temporal scales). Controls
            the GOP size. Examples: `l`=0 -> GOP_size = 1, `l`=1 ->
            GOP_size = 2, `l`=2 -> GOP_size = 4. etc.

    Returns
    -------

        None.

    '''
    
    #import ipdb; ipdb.set_trace()
    ir = image_io.ImageReader()
    iw = image_io.ImageWritter()
    pr = pyramid_io.PyramidReader()
    x = 2**l
    for j in range(l): # Number of temporal scales
        #import ipdb; ipdb.set_trace()
        A = pr.read(0, input)
        zero_L = np.zeros(A[0].shape, np.float64)
        zero_H = (zero_L, zero_L, zero_L)
        AL = _2D_iDWT(A[0], zero_H)
        AH = _2D_iDWT(zero_L, A[1])
        A = AL + AH
        iw.write(A, 0)
        i = 0
        while i < (n//x):
            B = pr.read(x*i+x//2, input)
            BL = _2D_iDWT(B[0], zero_H)
            rBH = _2D_iDWT(zero_L, B[1])
            C = pr.read(x*i+x, input)
            CL = _2D_iDWT(C[0], zero_H)
            CH = _2D_iDWT(zero_L, C[1])
            C = CL + CH
            iw.write(C, x*i+x, output)
            BHA = motion.motion_compensation(BL, AL, AH)
            BHC = motion.motion_compensation(BL, CL, CH)
            BH = rBH + (BHA + BHC) / 2
            B = BL + BH
            iw.write(B, x*i+x//2, output)
            AL = CL
            AH = CH
            i += 1
            print('i =', i)
        x //=2
