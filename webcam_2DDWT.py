import numpy as np
import cv2
#from filters.copy_frame import process_frame
from transform.dwt_color import forward as dwt
from transform.dwt_color import backward as idwt
from webcam import WebCam

class WebCam_2DDWT(WebCam):
    def process(self, frame):
        LL, H = dwt(frame)
        cv2.imshow('LL', LL.astype(np.uint8))
        cv2.imshow('LH', H[0].astype(np.uint8)*16+128)
        cv2.imshow('HL', H[1].astype(np.uint8)*16+128)
        cv2.imshow('HH', H[2].astype(np.uint8)*16+128)
        recons = idwt(LL, H)
        return recons.astype(np.uint8)

if __name__ == "__main__":
    driver = WebCam_2DDWT()
    driver.run()
