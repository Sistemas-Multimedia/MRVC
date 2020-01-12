# The prediction is base only on the right decomposition.

from MC.optical.motion import motion_estimation
from MC.optical.motion import estimate_frame

def generate_prediction(AL, BL, CL, AH, CH):
    flow_CL_BL = motion_estimation(CL, BL)
    BCH = estimate_frame(CH, flow_CL_BL)
    return BCH

