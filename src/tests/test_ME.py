#
# Testing the optical flow computation provided by OpenCV
#

import cv2
import numpy as np

def ME(frame1_path, frame2_path):
    '''
    Save frame1, frame 2 at file

        Calculate ME with calcOpticalFlowFarneback

    Export results in file sample/ME.txt

        return numpy.ndarray of Cartesian coordinate

    '''

    '''Read frame1'''
    frame1 = cv2.imread(frame1_path)
    np.savetxt('/tmp/frame1.txt', frame1.reshape(-1, frame1.shape[-1]), delimiter=',', fmt='%.18e')
    prvs = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)

    '''Read frame2'''
    frame2 = cv2.imread(frame2_path)
    np.savetxt('/tmp/frame2.txt', frame2.reshape(-1, frame2.shape[-1]), delimiter=',', fmt='%.18e')
    next = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)

    flow = cv2.calcOpticalFlowFarneback(prvs,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    return flow

'''Test, We use 2 image for this example'''
flow = ME("../images/000.png", "../images/001.png")
np.savetxt('/tmp/ME.txt',flow.reshape(-1,flow.shape[-1]), delimiter=',',fmt='%.18e')
#print(type(flow))
cv2.destroyAllWindows()
