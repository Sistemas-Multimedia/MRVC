import cv2
import numpy as np
import pywt
#import matplotlib.pyplot as plt

filter = 'db5'

frame = cv2.imread('../images/000.png')

#cv2.imshow('003', frame); cv2.waitKey(0); cv2.destroyAllWindows()
#cv2.imshow('003', frame[:,:,0]); cv2.waitKey(0); cv2.destroyAllWindows()

'''
pyramid = pywt.dwt2(frame, filter)
frame2 = pywt.idwt2(pyramid, filter)
'''

pyramid = [None]*3
for c in range(3):
    pyramid[c] = pywt.dwt2(frame[:,:,c], filter, mode='per')

tmp = [None]*3
for c in range(3):
    tmp[c] = pywt.idwt2(pyramid[c], filter, mode='per')

frame2 = np.empty((768,1280,3), dtype=np.uint8)

for c in range(3):
    frame2[:,:,c] = np.rint(tmp[c]).astype(np.uint8)

#for c in range(3):
#    for y in range(768):
#        for x in range(1280):
#            frame2[y,x,c] = int(round(tmp[c][y,x]))

#cv2.imshow('003', frame2); cv2.waitKey(0); cv2.destroyAllWindows()
#cv2.imshow('003', frame2[:,:,2]); cv2.waitKey(0); cv2.destroyAllWindows()
print((frame==frame2).all())

cv2.imwrite('/tmp/test_dwt_output.png',frame2)

