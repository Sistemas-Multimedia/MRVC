import numpy as np
import cv2
#from filters.copy_frame import process_frame
from transform.dwt_color import forward as dwt
from transform.dwt_color import backward as idwt
from webcam import WebCam

class WebCam_2DLPT(WebCam):
    def init_structures(self, y, x):
        self.zero_L = np.zeros((y, x), np.float64)
        
    def process(self, frame):
        LL, LH, HL, HH = dwt(frame)
        H = idwt(self.zero_L, LH, HL, HH)
        cv2.imshow('LL', LL.astype(np.uint8))
        cv2.imshow('H', H.astype(np.uint8)*16+128)
        _, LH, HL, HH = dwt(H)
        H = LH, HL, HH
        recons = idwt(LL, H)
        return recons.astype(np.uint8)

if __name__ == "__main__":
    driver = WebCam_2DLPT()
    
    driver.run()
