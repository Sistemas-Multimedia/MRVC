import cv2
import numpy as np
 
from matplotlib import pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
plt.rcParams.update({'figure.max_open_warning': 0})


def divimg(im,factor):
    #print(im)
    im2 = cv2.imread(im,cv2.COLOR_BGR2GRAY)
    plt.title(im)
    #plt.subplot(2, 2, 1)
    plt.imshow(im2)
    plt.show()
    
    a2 = np.true_divide(im2,factor)
    title=im+"factor"
    plt.title(title)
    #plt.subplot(2, 2, 2)
    #plt.figure()
    plt.imshow(a2)
    plt.show()
    
def divimgw(im,factor):
    im2 = cv2.imread(im,cv2.COLOR_BGR2GRAY)
    plt.imshow(im2)
    a2 = np.true_divide(im2,factor)
    #frame2 = np.empty((768,1280,3), dtype=np.uint8) 
    write_name="../imgf/f"+factor+im2
    cv2.imwrite(write_name, a2)