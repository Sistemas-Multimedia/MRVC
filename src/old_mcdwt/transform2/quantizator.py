import numpy as np


def quantizator(frame, coef):
    ''' Quantizator a frame

     Arguments
     ---------

         image
         coef for denominator


     Returns
     -------

         image divided by coef

     '''
    output = frame/coef
    '''cv2.imwrite("outputQcuant.png", output)'''


    return output


def unQuantizator(frame, coef):
    '''
    ----- Input
        Frame quantizated
        coef  multiply
        return numpy.ndarray of Cartesian coordinate
    '''
    output = frame*coef

    '''    cv2.imwrite("outputUncuantificator.png", output) '''
    return output
