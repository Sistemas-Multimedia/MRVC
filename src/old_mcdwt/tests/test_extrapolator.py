#!/usr/bin/env python3

import os
import sys
import cv2
import numpy as np
import tempfile as tf

sys.path.insert(0, '../mcdwt')
import extrapolator

input_path = '../images/000.png'
displacement = (100, 100)

print('Extrapolating image', input_path, 'with displacement', displacement)
base = cv2.imread(input_path)
result = extrapolator.extrapolate_frame(base, displacement)
output_path = os.path.join(tf.gettempdir(), 'extrapolated.png')
cv2.imwrite(output_path, result)
print('Extrapolated image written to', output_path)
