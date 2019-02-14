import cv2
import numpy as np
import os

class InputFileException(Exception):
    pass

def read(prefix = "../../sequences/stockholm/", suffix = "000.png"):
    '''Read a 3-components image from disk. Each component stores
       integers between [0, 65535].

    Parameters
    ----------

        image : str.

            Path to the image in the file system, without extension.

    Returns
    -------

        [:,:,:].

            A color image, where each component is in the range [-32768, 32767].

    '''
    fn = prefix + suffix
    image = cv2.imread(fn, -1)
    if image is None:
        raise InputFileException('IO::image:read: {} not found'.format(fn))
    else:
        if __debug__:
            print("IO::image:read: read {}".format(fn))
    buf = image.astype(np.float32)
    buf -= 32768.0
    return buf.astype(np.int16)

def write(image, prefix = "/tmp/", suffix = "000.png"):
    '''Write a 3-components image to disk. Each component stores integers
       between [0, 65536].

    Parameters
    ----------

        image : [:,:,:].

            The color image to write, where each component is in the range [-32768, 32768].

        file_name : str.

            Path to the image in the file system, without extension.

    Returns
    -------

        None.
    '''

    image = image.astype(np.float32)
    image += 32768.0
    image = image.astype(np.uint16)
    fn = prefix + suffix
    cv2.imwrite(fn, image)
    #cv2.imwrite(file_name, image)
    #os.rename(file_name + ".png", file_name)
    if __debug__:
        print("IO::image:write: written {}".format(fn))

if __name__ == "__main__":

    img = read("../../sequences/stockholm/", "000.png")
    write(img, "/tmp/", "000.png")
    print("IO::image:__main__: generated /tmp/000.png")
