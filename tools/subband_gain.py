import cv2
import numpy as np
import math
import argparse
from cv2 import Sobel
from skimage import data, draw, transform, util, color, filters
import pylab
sys.path.insert(0, "..")
from tools.show_statistics import calc_energy

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass

def main():
        parser = argparse.ArgumentParser(description = "Shows the subands gains\n\n"
                                        "Example:\n\n"
                                        "  python3 show_statistics.py -i ../tmp/scale1 -hh /tmp/000_HH\n",
                                        formatter_class=CustomFormatter)

        parser.add_argument("-hh", "--subband HH",
                        help="Subband HH to compare", default="/tmp/HH/000_LL")
        parser.add_argument("-i", "--Reconstructed image",
                        help="Reconstructed image with DWT backwards", default="/tmp/scale1")
                                        
                        
        args = parser.parse_args()

        # if args.hh != None:
        #     img_reconstructed = cv2.imread(args.hh)        

        # if args.i != None:
        #     img_bandHH = cv2.imread(args.i)
        # else:
        #     img_bandHH = img_reconstructed * 0

        img_reconstructed = cv2.imread("img") 
        img_bandHH = img_reconstructed

        
        img_bandHH[(img_bandHH.[0].count//2)][(img_bandHH.[1].count//2)][0] = 255
        img_bandHH[(img_bandHH.[0].count//2)][(img_bandHH.[1].count//2)][1] = 255
        img_bandHH[(img_bandHH.[0].count//2)][(img_bandHH.[1].count//2)][3] = 255

        gain = calc_energy(img_reconstructed)/ calc_energy(img_bandHH)

        #pylab.imshow(reconstructed), pylab.show()

        print("Shape: {}".format(img_reconstructed.shape))

        image_black = imagen * 0
        imageHH = imagen_negro

        print("Forma imagen en negro: {}".format(imagen.shape))




        pylab.imshow(imagenHH), pylab.show()

        imagen = cv2.imread(args.image)

        cv2.imwrite("black.png", imagenLH.astype(np.uint16))
        cv2.imwrite("imgHH.pnh", imagenHH.astype(np.uint16))





if __name__ == "__main__":
    main()
