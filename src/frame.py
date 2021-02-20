''' MRVC/frame.py '''

import numpy as np
import cv2
import colors

def read(prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}{ASCII_frame_number}.png"
    frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    try:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except cv2.error:
        print(colors.red(f'frame.read: Unable to read "{fn}"'))
        raise
    frame = np.array(frame, dtype=np.float64)
    #print(frame.shape)
    return frame # [rows, columns, components]

def _write(frame, prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}{ASCII_frame_number}.png"
    print(frame.shape, fn)
    frame = frame.astype(np.uint8)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(fn, frame)

def debug_write(frame, prefix, frame_number):
    if __debug__:
        _write(frame, prefix, frame_number)

def write(frame, prefix, frame_number):
    _write(frame, prefix, frame_number)
