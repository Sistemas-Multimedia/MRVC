import numpy as np
import cv2
import sys

sys.path.insert(0, "..")
sys.path.insert(1, "../..")
from DWT import DWT
from webcam import WebCam

class WebCam_2DLPT(WebCam):

    def __init__(self):
        super().__init__()
        self.dwt = DWT()
        self.zero_L = np.zeros((self.height//2, self.width//2, 3), np.float64)

    def process(self, frame):
        LL, H = self.dwt.forward(frame)
        _H = self.dwt.backward((self.zero_L, H))
        cv2.imshow('LL', LL.astype(np.uint8))
        cv2.imshow('H', _H.astype(np.uint8)*16+128)
        _, H = self.dwt.forward(_H)
        recons = self.dwt.backward((LL, H))
        return recons.astype(np.uint8)

if __name__ == "__main__":
    driver = WebCam_2DLPT()
    driver.run()
