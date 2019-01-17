import cv2
import numpy as np

from mcdwt.quantizator import quantizator, unQuantizator

coef = 64

frame = cv2.imread("../images/001.png")
outputQuantizated = quantizator(frame, coef)

cv2.imwrite("/tmp/001_quantized.png", outputQuantizated)

outputUnQuantizated = unQuantizator(outputQuantizated, coef)
cv2.imwrite("/tmp/001_unquantized.png", outputUnQuantizated)
