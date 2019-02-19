import sys
import cv2
import numpy as np

sys.path.insert(0, "..")
from src.old_mcdwt.transform2.quantizator import quantizator, unQuantizator

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
    parser = argparse.ArgumentParser(
        description = "Quantization image script\n\n"
        "Examples:\n\n"
        "  python3 -O quantization_image.py -i /tmp/image -c 64 -o /tmp/image_unquantized ",
        formatter_class=CustomFormatter)

   
    parser.add_argument("-i", "--image", help="Path of the input image")
    parser.add_argument("-c", "--coefficient", help="Quantization coefficient", default=64,type=int)
    parser.add_argument("-o", "--output", help="Output path", default="/tmp/001_unquantized.png")

    args = parser.parse_args()

coef = args.coefficient

frame = cv2.imread(args.image)
outputQuantizated = quantizator(frame, coef)

#Show the quantized image
#cv2.imwrite("/tmp/001_quantized.png", outputQuantizated)

outputUnQuantizated = unQuantizator(outputQuantizated, coef)
cv2.imwrite(args.output, outputUnQuantizated)


