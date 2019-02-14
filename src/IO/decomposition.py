import cv2
import numpy as np
import os
if __debug__:
    import time

class InputFileException(Exception):
    pass

def normalize(x):
    return ((x - np.amin(x)) / (np.amax(x) - np.amin(x)))

def readL(prefix = "/tmp/", image = "000", suffix = ".png"):
    '''Read a 3-components LL-subband from disk. Each component stores
       integers between [0, 65535].

    Parameters
    ----------

        file_name : str.

            Path to the LL-subband in the file system, without extension.

    Returns
    -------

        [:,:,:].

            A color image, where each component is in the range [-32768, 32767].

    '''
    #fn = os.path.dirname(file_name) + '/LL/' + os.path.basename(file_name)
    fn = prefix + "LL" + image + suffix
    LL = cv2.imread(fn, -1)
    if LL is None:
        raise InputFileException('IO::decomposition:readL: {} not found'.format(fn))
    else:
        if __debug__:
            print("IO::decomposition:readL: read {}".format(fn))
    LL = LL.astype(np.float32)
    LL -= 32768.0
    LL = LL.astype(np.int16)

    if __debug__:
        cv2.imshow("IO::decomposition:readL: LL subband", normalize(LL))

    if __debug__:
        while cv2.waitKey(1) & 0xFF != ord('q'):
            time.sleep(0.1)

    return LL

def readH(prefix = "/tmp/", image = "000", suffix = ".png"):
    #fn = os.path.dirname(file_name) + '/LH/' + os.path.basename(file_name)
    fn = prefix + "LH" + image + suffix
    LH = cv2.imread(fn, -1)
    if LH is None:
        raise InputFileException('IO::decomposition:readH: {} not found'.format(fn))
    else:
        if __debug__:
            print("IO::decomposition:readH: read {}".format(fn))
    LH = LH.astype(np.float32)
    LH -= 32768.0
    LH = LH.astype(np.int16)

    if __debug__:
        cv2.imshow("IO::decomposition:readH: LH subband", normalize(LH))

    #fn = os.path.dirname(file_name) + '/HL/' + os.path.basename(file_name)
    fn = prefix + "HL" + image + suffix
    HL = cv2.imread(fn, -1)
    if HL is None:
        raise InputFileException('IO::decomposition:readH: {} not found'.format(fn))
    else:
        if __debug__:
            print("IO::decomposition:readH: read {}".format(fn))
    HL = HL.astype(np.float32)
    HL -= 32768.0
    HL = HL.astype(np.int16)

    if __debug__:
        cv2.imshow("IO::decomposition:readH: HL subband", normalize(HL))

    #fn = os.path.dirname(file_name) + '/HH/' + os.path.basename(file_name)
    fn = prefix + "HH" + image + suffix
    HH = cv2.imread(fn, -1)
    if HH is None:
        raise InputFileException('IO::decomposition:readH: {} not found'.format(fn))
    else:
        if __debug__:
            print("IO::decomposition:readH: read {}".format(fn))
    HH = HH.astype(np.float32)
    HH -= 32768.0
    HH = HH.astype(np.int16)

    if __debug__:
        cv2.imshow("IO::decomposition:readH: HH subband", normalize(HH))

    if __debug__:
        while cv2.waitKey(1) & 0xFF != ord('q'):
            time.sleep(0.1)

    return LH, HL, HH

def read(prefix = "/tmp/", image = "000", suffix = ".png"):
    '''Read a decomposition from disk. The coefficients must be in the range [0, 65535].

    Parameters
    ----------

        file_name : str.

            Path to the decomposition in the file system, without extension.

    Returns
    -------

        (L, H) where L = [:,:,:] and H = (LH, HL, HH),
        where LH, HL, HH = [:,:,:]. The coefficients are in the range
        [-32768, 32767].

            A color decomposition.

    '''

    LL = readL(prefix, image, suffix)
    LH, HL, HH = readH(prefix, image, suffix)
    return (LL, (LH, HL, HH))

def writeL(LL, prefix = "/tmp/", image="000", suffix = ".png"):
    '''Write a LL-subband to disk.

    Parameters
    ----------

        LL : [:,:,:].

            An image structure.

        dir_name : str.

            Path to the LL subband.

    Returns
    -------

        None.

    '''

    LL = LL.astype(np.float32)
    LL += 32768.0
    LL = LL.astype(np.uint16)
    if __debug__:
        cv2.imshow("IO::decomposition:writeL: LL subband", normalize(LL))
    #path = os.path.dirname(file_name)
    #if __debug__:
    #    print("File: {}".format(file_name))
    #path += '/LL/'
    #if not os.path.exists(path):
    #    os.mkdir(path)
    #cv2.imwrite(path + os.path.basename(file_name) + ".png", LL)
    #os.rename(path + os.path.basename(file_name) + ".png", path + os.path.basename(file_name))
    fn = prefix + "LL" + image +  suffix
    cv2.imwrite(fn, LL)
    #os.rename(fn + ".png", fn)
    if __debug__:
        #print("IO::decomposition:writeL: written {}".format(path + os.path.basename(file_name)))
        print("IO::decomposition:writeL: written {}".format(fn))

    if __debug__:
        while cv2.waitKey(1) & 0xFF != ord('q'):
            time.sleep(0.1)

def writeH(H, prefix = "/tmp/", image = "000", suffix = ".png"):
    '''Write the high-frequency subbands H=(LH, HL, HH) to the disk.

    Parameters
    ----------

        dir_name : str.

            Path to the 3 subband files (LH.png, HL.png, and HH.png) in the file system.

    Returns
    -------

        None

    '''
    LH = H[0].astype(np.float32)
    LH += 32768.0
    LH = LH.astype(np.uint16)
    if __debug__:
        cv2.imshow("IO::decomposition:writeH: LH subband", normalize(LH))
    #path = os.path.dirname(file_name)
    #if __debug__:
    #    print("File Path: {}".format(path))
    #path += '/LH/'
    #if not os.path.exists(path):
    #    os.mkdir(path)
    #cv2.imwrite(path + os.path.basename(file_name) + ".png", LH)
    #os.rename(path + os.path.basename(file_name) + ".png", path + os.path.basename(file_name))
    fn = prefix + "LH" + image + suffix
    cv2.imwrite(fn, LH)
    #os.rename(fn + ".png", fn)
    if __debug__:
        #print("IO::decomposition:writeH: written {}".format(file_name))
        print("IO::decomposition:writeH: written {}".format(fn))

    HL = H[1].astype(np.float32)
    HL += 32768.0
    HL = HL.astype(np.uint16)
    if __debug__:
        cv2.imshow("IO::decomposition:writeH: HL subband", normalize(HL))
    #path = os.path.dirname(file_name)
    #path += '/HL/'
    #if not os.path.exists(path):
    #    os.mkdir(path)
    #cv2.imwrite(path + os.path.basename(file_name) + ".png", HL)
    #os.rename(path + os.path.basename(file_name) + ".png", path + os.path.basename(file_name))
    fn = prefix + "HL" + image + suffix
    cv2.imwrite(fn, HL)
    #os.rename(fn + ".png", fn)
    if __debug__:
        #print("IO::decomposition:writeH: written {}".format(file_name))
        print("IO::decomposition:writeH: written {}".format(fn))

    HH = H[2].astype(np.float32)
    HH += 32768.0
    HH = HH.astype(np.uint16)
    if __debug__:
        cv2.imshow("IO::decomposition:writeH: HH subband", normalize(HH))
    #path = os.path.dirname(file_name)
    #path += '/HH/'
    #if not os.path.exists(path):
    #    os.mkdir(path)
    #cv2.imwrite(path + os.path.basename(file_name) + ".png", HH)
    #os.rename(path + os.path.basename(file_name) + ".png", path + os.path.basename(file_name))
    fn = prefix + "HH" + image + suffix
    cv2.imwrite(fn, HH)
    #os.rename(fn + ".png", fn)
    if __debug__:
        #print("IO::decomposition:writeH: written {}".format(file_name))
        print("IO::decomposition:writeH: written {}".format(fn))

    if __debug__:
        while cv2.waitKey(1) & 0xFF != ord('q'):
            time.sleep(0.1)

def write(decomposition, prefix = "/tmp/", image = "000", suffix = ".png"):
    '''Write a decomposition to disk.

    Parameters
    ----------

        decomposition : (LL, (LH, HL, HH) where each subband is [:,:,:].

            Decomposition structure.

        dir_name : str.

            Decomposition in the file system.

    Returns
    -------

        None.

    '''

    writeL(decomposition[0], prefix, image, suffix)
    writeH(decomposition[1], prefix, image, suffix)

if __name__ == "__main__":

    import os
    os.system("cp ../../sequences/stockholm/000.png /tmp/LL000.png") # Use Python's call, not system's call
    os.system("cp ../../sequences/stockholm/001.png /tmp/LH000.png")
    os.system("cp ../../sequences/stockholm/002.png /tmp/HL000.png")
    os.system("cp ../../sequences/stockholm/003.png /tmp/HH000.png")
    pyr = read("/tmp/", "000", ".png")
    os.system("rm -rf /tmp/out/") # Use Python's call, not system's call
    os.mkdir("/tmp/out/")
    write(pyr, "/tmp/out/", "000", ".png")
    print("IO::decomposition:__main__: generated decomposition /tmp/out/000")
