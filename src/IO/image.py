import os
try:
    import cv2
except:
    os.system("pip3 install opencv-python --user")
try:
    import numpy as np
except:
    os.system("pip3 install numpy --user")

class InputFileException(Exception):
    pass

def read(prefix = "/tmp/", index = "000"):
    '''Read a 3-components image from disk. Each component stores
       integers between [0, 65535].

    Input:
    -----

        prefix: str.

            Path to the image in the file system, without extension.

    Output:
    ------

        (disk): [:,:,:].

            A color image, where each component is in the range
            [-32768, 32767].

    '''
    fn = prefix + index + ".png"
    image = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    #image = cv2.imread(fn, cv2.IMREAD_COLOR)
    if image is None:
        raise InputFileException('IO::image:read: {} not found'.format(fn))
    else:
        if __debug__:
            print("IO::image:read: read {}".format(fn))
    buf = image.astype(np.float32)
    buf -= 32768.0
    return buf.astype(np.int16)

def write(image, prefix = "/tmp/", index = "000"):
    '''Write a 3-components image to disk. Each component stores integers
       between [0, 65536].

    Input:
    -----

        image: [:,:,:].

            The color image to write, where each component is in the range [-32768, 32768].

        prefix: str.

            Path to the image in the file system, without extension.

    Output:
    ------

        (disk) : [:,:,:].

            A color image.
    '''

    image = image.astype(np.float32)
    image += 32768.0
    image = image.astype(np.uint16)
    fn = prefix + index + ".png"
    cv2.imwrite(fn, image)
    if __debug__:
        print("IO::image:write: written {}".format(fn))

if __name__ == "__main__":

    img = read("/tmp/", "000")
    write(img, "/tmp/", "000")
    print("IO::image:__main__: generated /tmp/000.png")
