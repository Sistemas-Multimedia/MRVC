from MC.optical.motion import motion_estimation
from MC.optical.motion import estimate_frame

def generate_prediction(AL, BL, CL, AH, CH):
    flow_AL_BL = motion_estimation(AL, BL)
    flow_CL_BL = motion_estimation(CL, BL)    
    BAH = estimate_frame(AH, flow_AL_BL)
    BCH = estimate_frame(CH, flow_CL_BL)
    BAL = estimate_frame(AL, flow_AL_BL)
    BCL = estimate_frame(CL, flow_CL_BL)
    EAL = BL - BAL
    ECL = BL - BCL
    SAL = 1/(1+abs(EAL))
    SCL = 1/(1+abs(ECL))
    return (BAH*SAL+BCH*SCL)/(SAL+SCL)
