import cv2
import numpy as np
#import pywt
#import matplotlib.pyplot as plt

image1 = cv2.imread('../input/000.png')
#print(type(image1))
image2 = cv2.imread('../input/001.png')

#image3=np.subtract(image1-image2)
image3=image2-image1

all_zeros=np.count_nonzero(image3)
print(all_zeros)
cv2.imwrite('../output/PNG/subtract58_56.png',image3)
