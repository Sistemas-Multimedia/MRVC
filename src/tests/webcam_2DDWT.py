import numpy as np
import cv2
import sys

sys.path.insert(0, "..")
sys.path.insert(1, "../..")
from DWT import DWT
from webcam import WebCam

#from filters.copy_frame import process_frame

class WebCam_2DDWT(WebCam):

    def __init__(self):
        super().__init__()
        self.dwt = DWT()

    def process(self, frame):
        LL, H = self.dwt.forward(frame)
        cv2.imshow('LL', LL.astype(np.uint8))
        cv2.imshow('LH', H[0].astype(np.uint8)*16+128)
        cv2.imshow('HL', H[1].astype(np.uint8)*16+128)
        cv2.imshow('HH', H[2].astype(np.uint8)*16+128)
        recons = self.dwt.backward((LL, H))
        return recons.astype(np.uint8)

if __name__ == "__main__":
    driver = WebCam_2DDWT()
    driver.run()
