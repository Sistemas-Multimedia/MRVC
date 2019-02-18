import cv2
import numpy as np
from matplotlib import pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})


def divimg(im,factor):
    #print(im)
    im2 = cv2.imread(im,cv2.COLOR_BGR2GRAY)
    plt.imshow(im2)
    a2 = np.true_divide(im2,factor)
    plt.figure()
    plt.subplot(2, 2, 1)
    plt.imshow(a2)