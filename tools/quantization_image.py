import sys
import cv2
import numpy as np

sys.path.insert(0, "..")

if __name__ == "__main__":

    import argparse

    class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
    parser = argparse.ArgumentParser(
        description = "Quantization image script\n\n"
        "Examples:\n\n"
        "  python3 -O quantization_image.py -i /tmp/image -s 24 -o /tmp/image_quantized ",
        formatter_class=CustomFormatter)

   
    parser.add_argument("-i", "--image", help="Path of the input image")
    parser.add_argument("-s", "--step", help="Quantization step", default=24,type=int)
    parser.add_argument("-o", "--output", help="Output path", default="/tmp/phaseII_unquantized.png")

    args = parser.parse_args()

step = args.step

frame = cv2.imread(args.image)
outputQuantizated = (frame / step).astype(np.int16)

#Show the quantized image
#cv2.imwrite("/tmp/phaseI_quantized.png", outputQuantizated)

outputUnQuantizated = (outputQuantizated * step).astype(np.int16)
cv2.imwrite(args.output, outputUnQuantizated)


