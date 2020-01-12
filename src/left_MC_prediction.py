# The prediction is based only on the left decomposition.

from MC.optical.motion import motion_estimation
from MC.optical.motion import estimate_frame

def generate_prediction(AL, BL, CL, AH, CH):
    flow_AL_BL = motion_estimation(AL, BL)
    BAH = estimate_frame(AH, flow_AL_BL)
    return BAH

