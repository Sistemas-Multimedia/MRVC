from MC.optical.motion import motion_estimation
from MC.optical.motion import estimate_frame

def predice(AL, BL, CL, AH, CH):
    
    if __debug__:
        print("Simple Average Prediction")

    flow = motion_estimation(AL, BL)
    flow = motion_estimation(CL, BL)
        
    BHC = estimate_frame(CH, flow)
    BLC = estimate_frame(CL, flow)

    BHA = estimate_frame(AH, flow)
    BLA = estimate_frame(AL, flow)


    return (BHA + BHC) / 2