''' MRVC/frame.py '''

import numpy as np
import cv2

def read(prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}{ASCII_frame_number}.png"
    frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.array(frame)
    #print(frame.shape)
    return frame # [rows, columns, components]

def write(frame, prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    cv2.imwrite(f"{prefix}{ASCII_frame_number}.png", frame)

