from MC.optical.motion import motion_estimation
from MC.optical.motion import estimate_frame
import sys
def generate_prediction(AL, BL, CL, AH, CH):
    flow_AL_BL = motion_estimation(AL, BL)
    flow_CL_BL = motion_estimation(CL, BL)
    BAH = estimate_frame(AH, flow_AL_BL)
    BCH = estimate_frame(CH, flow_CL_BL)
    return (BAH + BCH) / 2

