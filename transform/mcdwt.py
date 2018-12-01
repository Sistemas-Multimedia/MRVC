import cv2
import numpy as np
import pywt
import math
import sys

import transform import dwt_color as dwt
from mc.optical.motion import motion_compensation
sys.path.insert(0, "..")
from transform.io import image, pyramid

def forward_W():
    pass

def create_zero_subbands(self, dwtA):
    self.zero_L = np.zeros(dwtA[0].shape, np.float64)
    self.zero_H = (zero_L, zero_L, zero_L)
 
def forward_butterfly(self, AL, AH, BL, BH, CL, CH):
    dwtB = dwt.forward(A)
    BL = dwt.backward(dwtB[0], zero_H)
    BH = dwt.backward(zero_L, dwtB[1])
    dwtC = dwt.forward(C)
    CL = dwt.backward(dwtC[0], zero_H)
    CH = dwt.backward(zero_L, dwtC[1])
    BAH = motion_compensation(AL, BL, AH)
    BCH = motion_compensation(CL, BL, CL)
    prediction = (BAH + BCH) / 2
    rBH = BH - prediction
    #rBH = dwt.forward(rBH)
    return BL, rBH, CL, CH

def backward_butterfly(self, AL, AH, BL, BH C):
    A = AL + AH
    

def forward(prefix = "/tmp/", N = 5, K = 2):
    '''A Motion Compensated Discrete Wavelet Transform.

    Compute the 1D-DWT along motion trajectories. The input video (as
    a sequence of images) must be stored in disk (<input> directory)
    and the output (as a sequence of DWT coefficients that are called
    pyramids) will be stored in disk (<output> directory).

    Arguments
    ---------

        prefix : str

            Localization of the input/output images. Example:
            "/tmp/".

         N : int

            Number of images to process.

         K : int

            Number of leves of the MCDWT (temporal scales). Controls
            the GOP size. 

              K | GOP_size
            ----+-----------
              0 |        1
              1 |        2
              2 |        4
              3 |        8
              4 |       16
              5 |       32
              : |        :

    Returns
    -------

        None.

    '''
    
    # import ipdb; ipdb.set_trace()
    #k = 0
    for k in range(K): # spatial scale
        x = 2
        while x < N:
            i = 0 # first image of the butterfly
            A = image.read("{}{:03d}_{}".format(prefix, i, k))
            dwtA = dwt.forward(A)
            L_y = dwtA[0].shape[0]
            L_x = dwtA[0].shape[1]
            pyramid.write(dwtA, "{}{:03d}_{}".format(prefix, i, k+1))
            zero_L = np.zeros(dwtA[0].shape, np.float64)
            zero_H = (zero_L, zero_L, zero_L)
            AL = dwt.backward(dwtA[0], zero_H)
            if __debug__:
                image.write(AL, "{}{:03d}_{}".format(prefix + "_AL_", i, k))
            AH = dwt.backward(zero_L, dwtA[1])
            if __debug__:
                image.write(AH, "{}{:03d}_{}".format(prefix + "_AH_", i, k))
            while i < (N//x):
                print("k={} i={} x={} B={} C={}".format(k, i, x, x*i+x//2, x*i+x))
                B = image.read("{}{:03d}_{}".format(prefix, x*i+x//2, k))
                dwtB = dwt.forward(B)
                BL = dwt.backward(dwtB[0], zero_H)
                BH = dwt.backward(zero_L, dwtB[1])
                C = image.read("{}{:03d}_{}".format(prefix, x*i+x, k))
                dwtC = dwt.forward(C)
                pyramid.write(dwtC, "{}{:03d}_{}".format(prefix, x*i+x, k+1))
                CL = dwt.backward(dwtC[0], zero_H)
                if __debug__:
                    image.write(CL, "{}{:03d}_{}".format(prefix + "_CL_", x*i+x, k))
                CH = dwt.backward(zero_L, dwtC[1])
                if __debug__:
                    image.write(CH, "{}{:03d}_{}".format(prefix + "_CH_", x*i+x, k))

                if __debug__:
                    BLA = motion_compensation(AL, BL, AL)
                    BLC = motion_compensation(CL, BL, CL)
                    prediction = (BLA+BLC) / 2
                    image.write(prediction, "{}{:03d}_{}".format(prefix + "_prediction_L_", x*i+x//2, k))
                    
                BHA = motion_compensation(AL, BL, AH)
                BHC = motion_compensation(CL, BL, CH)
                if __debug__:
                    image.write(BH, "{}{:03d}_{}".format(prefix + "_BH_", x*i+x//2, k))
                prediction = (BHA + BHC) / 2
                if __debug__:
                    image.write(prediction, "{}{:03d}_{}".format(prefix + "_prediction_", x*i+x//2, k))
                rBH = BH - prediction
                if __debug__:
                    image.write(rBH, "{}{:03d}_{}".format(prefix + "_residue_", x*i+x//2, k))
                rBH = dwt.forward(rBH)
                rBH[0][0:L_y,0:L_x,:] = dwtB[0]
                pyramid.write(rBH, "{}{:03d}_{}".format(prefix, x*i+x//2, k+1))
                AL = CL
                AH = CH
                i += 1
            x *= 2

def backward(input = '/tmp/', output='/tmp/', N=5, S=2):
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

         N : int

            Number of pyramids to process.

         S : int

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
    x = 2**S
    for s in range(S): # Number of temporal scales
        #import ipdb; ipdb.set_trace()
        A = pr.read(0, input)
        zero_L = np.zeros(A[0].shape, np.float64)
        zero_H = (zero_L, zero_L, zero_L)
        AL = color_dwt.backward(A[0], zero_H)
        AH = color_dwt.backward(zero_L, A[1])
        A = AL + AH
        iw.write(A, 0, output)
        i = 0
        while i < (N//x):
            B = pr.read(x*i+x//2, input)
            BL = color_dwt.backward(B[0], zero_H)
            rBH = color_dwt.backward(zero_L, B[1])
            C = pr.read(x*i+x, input)
            CL = color_dwt.backward(C[0], zero_H)
            CH = color_dwt.backward(zero_L, C[1])
            C = CL + CH
            iw.write(C, x*i+x, output)
            BHA = motion_compensation.motion_compensation(BL, AL, AH)
            BHC = motion_compensation.motion_compensation(BL, CL, CH)
            BH = rBH + (BHA + BHC) / 2
            B = BL + BH
            iw.write(B, x*i+x//2, output)
            AL = CL
            AH = CH
            i += 1
            print('i =', i)
        x //=2
