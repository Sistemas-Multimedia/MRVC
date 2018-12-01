import cv2


class InputFileException(Exception):
    pass


class ImageReader:
    '''Read PNG images from disk.
    
    Images must be enumerated. Example: "image000.png, image001.png,
    ..."

    '''

    def __init__(self):
        pass

    def read(self, number, path='./'):
        '''Read an image from disk.

        Parameters
        ----------

            number : int.

                Index of the image in the sequence.

            path : str.

                Image path.

        Returns
        -------

            [:,:,:].

                A color image.

        '''

        file_name = '{}{:03d}.png'.format(path, number)
        image = cv2.imread(file_name, -1)
        if image is None:
            raise InputFileException('{} not found'.format(file_name))
        else:
            image -= 32768
            return image


class ImageWritter:
    '''Write PNG images to disk.

    Images should be enumerated. Example: "image000.png, image001.png, ..."

    '''

    def __init__(self):
        pass

    def write(self, image, number=0, path='./'):
        '''Write an image to disk.

        Parameters
        ----------

            image : [:,:,:].

                The color image to write.

            number : int.

                Index of the image in the sequence.

            path : str.

                Path to the image.

        Returns
        -------

            None.

        '''

        file_name = '{}{:03d}.png'.format(path, number)

        image += 32768
        
        assert (np.amax(image) < 65536), '16 bit unsigned int range overflow'
        assert (np.amin(image) >= 0), '16 bit unsigned int range underflow'
        
        #for y in range(image.shape[0]):
        #    for x in range(image.shape[1]):
        #        for c in range(image.shape[2]):
        #            if image[y,x,c] < 0:
        #                print(image[y,x,c])

        cv2.imwrite(file_name, np.rint(image).astype(np.uint16))
