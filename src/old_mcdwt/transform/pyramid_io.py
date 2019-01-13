import math
import cv2
import numpy as np

class InputFileException(Exception):
    pass

class PyramidReader:
    '''Read PNG pyramids from disk.

    Pyramids should be enumerated. Example: "pyramid000.png,
    pyramid001.png, ..."

    '''

    def __init__(self):
        pass

    def read(self, number=0, path='./'):
        '''Read a pyramid from disk.

        Parameters
        ----------

            number : int.

                Index of the pyramid in the sequence.

            path : str.

                Path to the pyramid.

        Returns
        -------

            (L,H) where L=[:,:,:] and H=(LH,HL,HH), where LH,HL,HH=[:,:,:].

                A color pyramid.

        '''

        file_name = '{}{:03d}L.png'.format(path, number)
        LL = cv2.imread(file_name, -1).astype('float64')
        LL -= 32768
        if LL is None:
            raise InputFileException('{} not found'.format(file_name))
        file_name = '{}{:03d}H.png'.format(path, number)
        buf = cv2.imread(file_name, -1).astype('float64')
        if buf is None:
            raise InputFileException('{} not found'.format(file_name))
        else:
            y = math.ceil(buf.shape[0]/2)
            x = math.ceil(buf.shape[1]/2)
            LH = buf[0:y,x:buf.shape[1],:]
            LH -= 32768
            HL = buf[y:buf.shape[0],0:x,:]
            HL -= 32768
            HH = buf[y:buf.shape[0],x:buf.shape[1],:]
            HH -= 32768
            return (LL, (LH, HL, HH))
        
class PyramidWritter:
    '''Write PNG pyramids to disk.

    Pyramids must be enumerated. Example: "pyramid000{L|H}.png,
    pyramid001{L|H}.png, ...", being 'L' used for the low-frequency
    subband LL and H for the subbands LH, HL and HH.

    '''

    def __init__(self):
        pass

    def write(self, pyramid, number=0, path='./'):
        '''Write a pyramid to disk.

        Parameters
        ----------

            L : [:,:,:].

                LL subband.

            H : (LH, HL, HH), where LH,HL,HH=[:,:,:].

                H subbands.

            number : int.

                Index of the pyramid in the sequence.

            path : str.

                Path to the pyramid.

        Returns
        -------

            None.

        '''
        #import ipdb; ipdb.set_trace()
        file_name = '{}{:03d}L.png'.format(path, number)
        LL = pyramid[0] + 32768

        assert (np.amax(LL) < 65536), 'range overflow'
        assert (np.amin(LL) >= 0), 'range underflow'
        #for yy in range(LL.shape[0]):
        #    for xx in range(LL.shape[1]):
        #        for cc in range(LL.shape[2]):
        #            if (LL[yy,xx,cc] < 0) | (LL[yy,xx,cc] > 65535):
        #                print(LL[yy,xx,cc])

        LL = np.rint(LL).astype('uint16')
        cv2.imwrite(file_name, LL)
        y = pyramid[0].shape[0]
        x = pyramid[0].shape[1]
        buf = np.full((y*2, x*2, 3), 32768, np.uint16)
        #buf[0:y,x:x*2,:] = np.round(pyramid[1][0] + 128)
        #buf[y:y*2,0:x,:] = np.round(pyramid[1][1] + 128)
        #buf[y:y*2,x:x*2,:] = np.round(pyramid[1][2] + 128)
        LH = pyramid[1][0] + 32768

        assert (np.amax(LH) < 65536), 'range overflow'
        assert (np.amin(LH) >= 0), 'range underflow'
        #for yy in range(LH.shape[0]):
        #    for xx in range(LH.shape[1]):
        #        for cc in range(LH.shape[2]):
        #            if (LH[yy,xx,cc] < 0) | (LH[yy,xx,cc] > 65535):
        #                print(LH[yy,xx,cc])

        buf[0:y,x:x*2,:] = np.rint(LH).astype('uint16')
        HL = pyramid[1][1] + 32768

        assert (np.amax(HL) < 65536), 'range overflow'
        assert (np.amin(HL) >= 0), 'range underflow'
        #for yy in range(HL.shape[0]):
        #    for xx in range(HL.shape[1]):
        #        for cc in range(HL.shape[2]):
        #            if (HL[yy,xx,cc] < 0) | (HL[yy,xx,cc] > 65535):
        #                print(HL[yy,xx,cc])

        buf[y:y*2,0:x,:]= np.rint(HL).astype('uint16')
        HH = pyramid[1][2] + 32768

        assert (np.amax(HH) < 65536), 'range overflow'
        assert (np.amin(HH) >= 0), 'range underflow'
        #for yy in range(HH.shape[0]):
        #    for xx in range(HH.shape[1]):
        #        for cc in range(HH.shape[2]):
        #            if (HH[yy,xx,cc] < 0) | (HH[yy,xx,cc] > 65535):
        #                print(HH[yy,xx,cc])
        
        buf[y:y*2,x:x*2,:] = np.rint(HH).astype('uint16')
        file_name = '{}{:03d}H.png'.format(path, number)
        
        cv2.imwrite(file_name, buf)
