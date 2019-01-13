import cv2
import numpy as np

class InputFileException(Exception):
    pass

def read(file_name):
    '''Read an image from disk.

    Parameters
    ----------

        image : str.

            Image in the file system, without extension.

    Returns
    -------

        [:,:,:].

            A color image.

    '''

    file_name += "_LL.png"
    image = cv2.imread(file_name, -1)
    if image is None:
        raise InputFileException('{} not found'.format(file_name))
    else:
        buf = image.astype(np.float64)
        buf -= 32768
        assert (np.amax(buf) < 32767), 'range overflow'
        assert (np.amin(buf) >= -32768), 'range underflow'
        return buf

def write(image, file_name):
    '''Write an image to disk.

    Parameters
    ----------

        image : [:,:,:].

            The color image to write.

        file_name : str.

            Image in the file system, without extension.

    Returns
    -------

        None.

    '''

    tmp = np.copy(image)
    tmp += 32768

    assert (np.amax(tmp) < 65536), '16 bit unsigned int range overflow'
    assert (np.amin(tmp) >= 0), '16 bit unsigned int range underflow'

    cv2.imwrite(file_name + "_LL.png", np.rint(tmp).astype(np.uint16))
