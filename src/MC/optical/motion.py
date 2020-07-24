import numpy as np
import cv2

def generate_prediction(reference, predicted, base):
    flow = motion_estimation(reference, predicted)
    return estimate_frame(base, flow)

def motion_estimation(reference, predicted):
    reference_0 = cv2.split(reference)[0] # Si trabajamos con YUV, podemos poner cv2.split(...)[0]
    predicted_0 = cv2.split(predicted)[0]
    return cv2.calcOpticalFlowFarneback(predicted_0, reference_0, None, 0.5, 3, 15, 3, 5, 1.2, 0) # Ojo, está al revés
    #return cv2.calcOpticalFlowFarneback(reference_y, predicted_y, None, 0.5, 3, 15, 3, 5, 1.2, 0)

def estimate_frame(base, flow):
    height, width = flow.shape[:2]
    map_x = np.tile(np.arange(width), (height, 1))
    map_y = np.swapaxes(np.tile(np.arange(height), (width, 1)), 0, 1)
    map_xy = (flow + np.dstack((map_x, map_y))).astype('float32')

    return cv2.remap(base, map_xy, None, 
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE)
