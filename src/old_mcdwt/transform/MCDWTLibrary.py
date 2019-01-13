import numpy as np
import cv2
import pywt

def split_video_in_frames_to_disk(filename):
    '''
    Reads a video file frame by frame, convert each frame to
    YCrCb and saves it in the folder /output as a binaryfile with
    .npy extension.
    '''
    cap = cv2.VideoCapture(filename)
    num_frame = 0

    while(cap.isOpened()):

        ret, frame = cap.read()
        if frame is None:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)


        cv2.imwrite('images/'+str(num_frame)+'.png',image)
        
        num_frame = num_frame + 1


def read_frame(filename):
    '''
    Reads a frame from a filename.
    '''

    # To see it in RGB uncomment the next line
    # image = cv2.cvtColor(image, cv2.COLOR_YCrCb2BGR)

    return cv2.imread(filename,1)


def image_y_to_four_bands(image):
    coeffs = pywt.dwt2(image, 'haar')
    return coeffs[0], coeffs[1][0], coeffs[1][1], coeffs[1][2],

def generate_x(ll, hl, lh, hh): 
    height = ll.shape[0]*2
    width = ll.shape[1]*2
    z = np.zeros((height//2, width//2), dtype="float64")
    il = pywt.idwt2((ll, (z, z, z)), 'haar')
    ih = pywt.idwt2((z, (hl, lh, hh)), 'haar')
    return il, ih

def output_from_dwt(ll, hl, lh, hh): 
    height = ll.shape[0]*2
    width = ll.shape[1]*2
    output = np.zeros((height, width), dtype="int16")
    output[0:height//2, 0:width//2] = ll
    output[0:height//2, width//2:width] = hl
    output[height//2:height, 0:width//2] = lh
    output[height//2:height, width//2:width] = hh
    return output

def forward_MCDWT(imageA, imageB, imageC):

    All, Ahl, Alh, Ahh = image_y_to_four_bands(imageA[:,:,0],)
    Bll, Bhl, Blh, Bhh = image_y_to_four_bands(imageB[:,:,0],)
    Cll, Chl, Clh, Chh = image_y_to_four_bands(imageC[:,:,0],)
        
    iAl, iAh = generate_x(All, Ahl, Alh, Ahh) 
    iBl, iBh = generate_x(Bll, Bhl, Blh, Bhh) 
    iCl, iCh = generate_x(Cll, Chl, Clh, Chh) 

    waste_image = iBh-((iAh + iCh)/2)
    Rll, Rhl, Rlh, Rhh = image_y_to_four_bands(waste_image)
    Rll = Bll
    outputA = output_from_dwt(All, Ahl, Alh, Ahh)
    outputR = output_from_dwt(Rll, Rhl, Rlh, Rhh)
    outputC = output_from_dwt(Cll, Chl, Clh, Chh)

    return outputA, outputR, outputC

def normalize_uint16_to_uint8(image):
    image = 256*((image+512)/1024)
    return np.uint8(image)

def video_converter (file_in, file_out):

    cap = cv2.VideoCapture(file_in)
    ret, frame1 = cap.read()

    fourcc = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter(file_out,fourcc, 50.0, (frame1.shape[0],frame1.shape[1]), False)


    while(cap.isOpened()):

        ret, frame2 = cap.read()
        ret, frame3 = cap.read()
        
        if frame3 is None or frame2 is None or frame3 is None :
            break
        image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2YCrCb)
        image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2YCrCb)
        image3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2YCrCb)

        image1, image2, image3 = forward_MCDWT(image1,image2,image3)

        out.write(normalize_uint16_to_uint(image1))
        out.write(normalize_uint16_to_uint(image2))
        out.write(normalize_uint16_to_uint(image3))
        frame1 = frame3

    cap.release()
    out.release()
