import math
import cv2
import numpy as np

class InputFileException(Exception):
    pass

def read(file_name):
    '''Read a pyramid from disk.

    Parameters
    ----------

        image : str.

            Pyramid in the file system, without extension.

    Returns
    -------

        (L, H) where L = [:,:,:] and H = (LH, HL, HH),
        where LH, HL, HH = [:,:,:].

            A color pyramid.

    '''

    LL = cv2.imread(file_name + "_LL.png", -1).astype(np.float64)
    LL -= 32768
    if LL is None:
        raise InputFileException('{} not found'.format(file_name + "_LL.png"))
    LH = cv2.imread(file_name + "_LH.png", -1).astype(np.float64)
    if LH is None:
        raise InputFileException('{} not found'.format(file_name + "_LH.png"))
    else:
        #y = math.ceil(buf.shape[0]/2)
        #x = math.ceil(buf.shape[1]/2)
        #LH = buf[0:y,x:buf.shape[1],:]
        LH -= 32768
    HL = cv2.imread(file_name + "_HL.png", -1).astype(np.float64)
    if HL is None:
        raise InputFileException('{} not found'.format(file_name + "_HL.png"))
    else:
        #HL = buf[y:buf.shape[0],0:x,:]
        HL -= 32768
    HH = cv2.imread(file_name + "_HH.png", -1).astype(np.float64)
    if HH is None:
        raise InputFileException('{} not found'.format(file_name + "_HH.png"))
    else:
        #HH = buf[y:buf.shape[0],x:buf.shape[1],:]
        HH -= 32768
        return (LL, (LH, HL, HH))

def write(pyramid, file_name):
    '''Write a pyramid to disk.

    Parameters
    ----------

        L : [:,:,:].

            A LL subband.

        H : (LH, HL, HH), where LH, HL, HH = [:,:,:].

            H subbands.

        file_name : str.

            Pyramid in the file system.

    Returns
    -------

        None.

    '''

    #file_name = '{}L{:03d}.png'.format(path, number)
    LL = pyramid[0] + 32768

    assert (np.amax(LL) < 65536), 'range overflow'
    assert (np.amin(LL) >= 0), 'range underflow'

    LL = np.rint(LL).astype(np.uint16)
    cv2.imwrite(file_name + "_LL.png", LL)
    #y = pyramid[0].shape[0]
    #x = pyramid[0].shape[1]
    #buf = np.full((y*2, x*2, 3), 32768, np.uint16)
    #buf[0:y,x:x*2,:] = np.round(pyramid[1][0] + 128)
    #buf[y:y*2,0:x,:] = np.round(pyramid[1][1] + 128)
    #buf[y:y*2,x:x*2,:] = np.round(pyramid[1][2] + 128)
    LH = pyramid[1][0] + 32768

    assert (np.amax(LH) < 65536), 'range overflow'
    assert (np.amin(LH) >= 0), 'range underflow'

    LH = np.rint(LH).astype(np.uint16)
    cv2.imwrite(file_name + "_LH.png", LH)
    
    #buf[0:y,x:x*2,:] = np.rint(LH).astype('uint16')
    
    HL = pyramid[1][1] + 32768

    assert (np.amax(HL) < 65536), 'range overflow'
    assert (np.amin(HL) >= 0), 'range underflow'

    HL = np.rint(HL).astype(np.uint16)
    cv2.imwrite(file_name + "_HL.png", HL)
    
    #buf[y:y*2,0:x,:]= np.rint(HL).astype('uint16')
    
    HH = pyramid[1][2] + 32768

    assert (np.amax(HH) < 65536), 'range overflow'
    assert (np.amin(HH) >= 0), 'range underflow'

    HH = np.rint(HH).astype(np.uint16)
    cv2.imwrite(file_name + "_HH.png", HH)
    
    #buf[y:y*2,x:x*2,:] = np.rint(HH).astype('uint16')
    #file_name = '{}H{:03d}.png'.format(path, number)

    #cv2.imwrite(file_name, buf)
