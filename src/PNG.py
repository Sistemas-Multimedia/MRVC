#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

''' MRVC/PNG.py '''

import cv2
import numpy as np
    
class PNG():

    def load_frame(self, prefix):
        fn = f"{prefix}.png"
        frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED) # [rows, columns, components]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.array(frame)
        frame = frame.astype(np.float32) - 32768.0
        return frame

    def write_frame(self, frame, prefix):
        frame = frame.astype(np.float32)
        frame += 32768.0
        frame = frame.astype(np.uint16)
        cv2.imwrite(f"{prefix}.png", frame)
