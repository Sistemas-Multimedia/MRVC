import cv2
import numpy as np
import math
import argparse
from cv2 import Sobel
from skimage import data, draw, transform, util, color, filters
import pylab

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

parser = argparse.ArgumentParser(description = "Displays information about an image\n\n"
                                 "Example:\n\n"
                                 "  python show_statistics.py -i ../sequences/stockholm/000\n",
                                 formatter_class=CustomFormatter)

parser.add_argument("-i", "--image",
                    help="Input image", default="/tmp/stockholm/000")

args = parser.parse_args()

imagen = cv2.imread(args.image)
pylab.imshow(imagen), pylab.show()

print("Forma de la imagen: {}".format(imagen.shape))

imagen_negro = imagen * 0

print("imagen en negro: {}".format(imagen.shape))

pylab.imshow(imagen), pylab.show()

imagenLH = imagen * 0
imagenHH = imagen * 0
imagenHL = imagen * 0
imagenLL = imagen * 0

print(imagenLH.shape)

imagenHH[80][150][0] = 255
imagenHH[80][150][1] = 255
imagenHH[80][150][2] = 255

pylab.imshow(imagenHH), pylab.show()

imagen = cv2.imread(args.image)

cv2.imwrite("imgLH", imagenLH.astype(np.uint16))
cv2.imwrite("imgHL", imagenHL.astype(np.uint16))
cv2.imwrite("imgHH", imagenHH.astype(np.uint16))
cv2.imwrite("imgLL", imagenLL.astype(np.uint16))





print("fin del script")

