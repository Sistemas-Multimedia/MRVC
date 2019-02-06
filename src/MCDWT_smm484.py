#!/usr/bin/env python

# import cv2
# import numpy as np
# import pywt
# import math

#import cv2
import numpy as np
import sys

from DWT import DWT
sys.path.insert(0, "..")
from src.IO import image
from src.IO import decomposition
from MC.optical.motion import generate_prediction
from MC.optical.motion import motion_estimation
from MC.optical.motion import estimate_frame

class MCDWT:

    def __init__(self, shape):
        self.zero_L = np.zeros(shape, np.float64)
        self.zero_H = (self.zero_L, self.zero_L, self.zero_L)
        self.dwt = DWT()

    def __forward_butterfly(self, aL, aH, bL, bH, cL, cH):
        '''Motion compensated forward MCDWT butterfly.

        Input:
        -----

        aL, aH, bL, bH, cL, cH: array[y, x, component], the decomposition of
        the images a, b and c.

        Output:
        ------

        residue_bH: array[y, x, component], the base of the decomposition of
        the residue fot the image b.

        '''

        AL = self.dwt.backward((aL, self.zero_H))
        BL = self.dwt.backward((bL, self.zero_H))
        CL = self.dwt.backward((cL, self.zero_H))
        AH = self.dwt.backward((self.zero_L, aH))
        BH = self.dwt.backward((self.zero_L, bH))
        CH = self.dwt.backward((self.zero_L, cH))

        '''
        Cálculo BHA, BLA, BHC, BLC optimizado
        '''
        flow = motion_estimation(AL, BL)
        BHA = estimate_frame(AH, flow)
        BLA = estimate_frame(AL, flow)
        flow = motion_estimation(CL, BL)
        BHC = estimate_frame(CH, flow)
        BLC = estimate_frame(CL, flow)
     
        if args.predictionerror == 2: 
            ELA = BL - BLA
            ELC = BL - BLC
            '''Modificación para corregir la división por 0'''
            SLA = 1 / (1+abs(ELA))
            SLC = 1 / (1+abs(ELC))
         
            prediction_BH = (BHA*SLA + BHC*SLC)/(SLA + SLC)

            '''
            Fin Nueva Predicción BH
            '''
        else:
            prediction_BH = (BHA + BHC) / 2

        residue_BH = BH - prediction_BH
        residue_bH = self.dwt.forward(residue_BH)
        return residue_bH[1]

    def __backward_butterfly(self, aL, aH, bL, residue_bH, cL, cH):
        AL = self.dwt.backward((aL, self.zero_H))
        BL = self.dwt.backward((bL, self.zero_H))
        CL = self.dwt.backward((cL, self.zero_H))
        AH = self.dwt.backward((self.zero_L, aH))
        residue_BH = self.dwt.backward((self.zero_L, residue_bH))
        CH = self.dwt.backward((self.zero_L, cH))
        
        '''
        Cálculo BHA, BLA, BHC, BLC optimizado
        '''
        flow = motion_estimation(AL, BL)
        BHA = estimate_frame(AH, flow)
        BLA = estimate_frame(AL, flow)
        flow = motion_estimation(CL, BL)
        BHC = estimate_frame(CH, flow)
        BLC = estimate_frame(CL, flow)

        if args.predictionerror == 2: 
            ELA = BL - BLA
            ELC = BL - BLC
            '''Modificación corregir la división por 0'''
            SLA = 1 / (1+abs(ELA))
            SLC = 1 / (1+abs(ELC))
         
            prediction_BH = (BHA*SLA + BHC*SLC)/(SLA + SLC)

            '''
            Fin Nueva Predicción BH
            '''
        else:
            prediction_BH = (BHA + BHC) / 2
        BH = residue_BH + prediction_BH
        bH = self.dwt.forward(BH)
        return bH[1]

    def forward(self, s="/tmp/stockholm_", S="/tmp/mc_stockholm_", N=5, T=2):
        '''A Motion Compensated Discrete Wavelet Transform.

        Compute the MC 1D-DWT. The input video s (as a sequence of
        1-levels decompositions) must be stored in disk and the output (as a
        1-levels MC decompositions) will be stored in S.

        Imput:
        -----

            prefix : s

                Localization of the input images. Example: "/tmp/stockholm_".

             N : int

                Number of images to process.

             T : int

                Number of levels of the MCDWT (temporal scales). Controls
                the GOP size.

                  T | GOP_size
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

            prefix : S

                Localization of the output decompositions. For example:
                "/tmp/mc_stockholm_".

        '''
        x = 2
        for t in range(T): # Temporal scale
            i = 0
            aL, aH = decomposition.read("{}{:03d}".format(s, 0))
            decomposition.write((aL, aH), "{}{:03d}".format(S, 0))
            while i < (N//x):
                bL, bH = decomposition.read("{}{:03d}".format(s, x*i+x//2))
                cL, cH = decomposition.read("{}{:03d}".format(s, x*i+x))
                bH = self.__forward_butterfly(aL, aH, bL, bH, cL, cH)
                decomposition.write((bL, bH), "{}{:03d}".format(S, x*i+x//2))
                decomposition.write((cL, cH), "{}{:03d}".format(S, x*i+x))
                aL, aH = cL, cH
                i += 1
            x *= 2

    def backward(self, S="/tmp/mc_stockholm_", s="/tmp/stockholm_", N=5, T=2):
        x = 2**T
        for t in range(T): # Temporal scale
            i = 0
            aL, aH = decomposition.read("{}{:03d}".format(S, 0))
            decomposition.write((aL, aH), "{}{:03d}".format(s, 0))
            while i < (N//x):
                bL, bH = decomposition.read("{}{:03d}".format(S, x*i+x//2))
                cL, cH = decomposition.read("{}{:03d}".format(S, x*i+x))
                bH = self.__backward_butterfly(aL, aH, bL, bH, cL, cH)
                decomposition.write((bL, bH), "{}{:03d}".format(s, x*i+x//2))
                decomposition.write((cL, cH), "{}{:03d}".format(s, x*i+x))
                aL, aH = cL, cH
                i += 1
            x //=2

    # Ignore
    def forward_(prefix = "/tmp/", N = 5, K = 2):
        '''A Motion Compensated Discrete Wavelet Transform.

        Compute the MC 1D-DWT. The input video (as a sequence of images)
        must be stored in disk (<input> directory) and the output (as a
        sequence of DWT coefficients that are called decompositions) will be
        stored in disk (<output> directory).

        Arguments
        ---------

            prefix : str

                Localization of the input/output images. Example:
                "/tmp/".

             N : int

                Number of images to process.

             K : int

                Number of levels of the MCDWT (temporal scales). Controls
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
                decomposition.write(dwtA, "{}{:03d}_{}".format(prefix, i, k+1))
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
                    decomposition.write(dwtC, "{}{:03d}_{}".format(prefix, x*i+x, k+1))
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
                    decomposition.write(rBH, "{}{:03d}_{}".format(prefix, x*i+x//2, k+1))
                    AL = CL
                    AH = CH
                    i += 1
                x *= 2

    # Ignore
    def backward_(input = '/tmp/', output='/tmp/', N=5, S=2):
        '''A (Inverse) Motion Compensated Discrete Wavelet Transform.

        iMCDWT is the inverse transform of MCDWT. Inputs a sequence of
        decompositions and outputs a sequence of images.

        Arguments
        ---------

            input : str

                Path where the input decompositions are. Example:
                "../input/image".

            output : str

                Path where the (inversely transformed) images will
                be. Example: "../output/decomposition".

             N : int

                Number of decompositions to process.

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
        pr = decomposition_io.DecompositionReader()
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

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

#        "  yes | cp -rf ../sequences/stockholm/ /tmp/\n"
    parser = argparse.ArgumentParser(
        description = "Motion Compensated 2D Discrete Wavelet (color) Transform\n\n"
        "Examples:\n\n"
        "  rm -rf /tmp/stockholm/\n"
        "  cp -r ../sequences/stockholm/ /tmp/\n"
        "  ./MDWT.py     -i /tmp/stockholm/ -d /tmp/stockholm_\n"
        "  ./MCDWT.py    -d /tmp/stockholm_ -m /tmp/mc_stockholm_ # Forward transform\n"
        "  ./MCDWT.py -b -d /tmp/stockholm_ -m /tmp/mc_stockholm_ # Backward transform\n"
        "  ./MDWT.py  -b -i /tmp/stockholm_ -d /tmp/stockholm_\n",
        formatter_class=CustomFormatter)

    parser.add_argument("-b", "--backward", action='store_true',
                        help="Performs backward transform")

    parser.add_argument("-d", "--decompositions",
                        help="Sequence of decompositions", default="/tmp/stockholm_")

    parser.add_argument("-m", "--mc_decompositions",
                        help="Sequence of motion compensated decompositions", default="/tmp/mc_stockholm_")

    parser.add_argument("-N",
                        help="Number of decompositions", default=5, type=int)

    parser.add_argument("-T",
                        help="Number of temporal levels", default=2, type=int)

    parser.add_argument("-e", "--predictionerror", default=1, type=int)  

    args = parser.parse_args()

    

    if args.backward:
        if __debug__:
            print("Backward transform")

        p = decomposition.readL("{}000".format(args.mc_decompositions))
        d = MCDWT(p.shape)

        d.backward(args.mc_decompositions, args.decompositions, args.N, args.T)
    else:
        if __debug__:
            print("Forward transform")

        p = decomposition.readL("{}000".format(args.decompositions))
        d = MCDWT(p.shape)

        p = d.forward(args.decompositions, args.mc_decompositions, args.N, args.T)
