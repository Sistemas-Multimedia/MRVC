import unittest
import sys
sys.path.append('../mcdwt')
import subprocess
#import MCDWTLibrary.py as ML
from mcdwt import MCDWTLibrary as ML
from mcdwt import transform_step as M
#import MCDWT.py as M
import cv2

class Test_Video_MCDWT(unittest.TestCase):

    def test_video(filename):
        '''
        Compare output video after running MCDWT and iMCDWT are working
        properly.

        '''

        subprocess.call(["mkdir", "/tmp/out"])

        #ML.split_video_in_frames_to_disk(filename)
        M.forward(input='../images/', output='/tmp/', n=5, l=2)
        M.backward(input='/tmp/', output='/tmp/out', n=5, l=2)

        #### MAYBE THIS IS WRONG ??
        diff_total000 = cv2.absdiff('images/000.png', '/tmp/out/000.png')
        diff_total001 = cv2.absdiff('images/001.png', '/tmp/out/001.png')
        diff_total002 = cv2.absdiff('images/002.png', '/tmp/out/002.png')
        diff_total003 = cv2.absdiff('images/003.png', '/tmp/out/003.png')
        diff_total004 = cv2.absdiff('images/004.png', '/tmp/out/004.png')
        ####

        value0 = assertIs(diff_total000, 0)
        value1 = assertIs(diff_total001, 0)
        value2 = assertIs(diff_total002, 0)
        value3 = assertIs(diff_total003, 0)
        value4 = assertIs(diff_total004, 0)

        print(str(value0))
        print(str(value1))
        print(str(value2))
        print(str(value3))
        print(str(value4))

if __name__== '__main__':
	unittest.main()
