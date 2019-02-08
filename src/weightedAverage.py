from MC.optical.motion import motion_estimation
from MC.optical.motion import estimate_frame

def predice(AL, BL, CL, AH, CH):
   
    if __debug__:
        print("Weighted Average Prediction")

    flow = motion_estimation(AL, BL)
    flow = motion_estimation(CL, BL)
        
    BHC = estimate_frame(CH, flow)
    BLC = estimate_frame(CL, flow)

    BHA = estimate_frame(AH, flow)
    BLA = estimate_frame(AL, flow)

    ELA = BL - BLA
    ELC = BL - BLC
    SLA = 1/(1+abs(ELA))
    SLC = 1/(1+abs(ELC))


    return (BHA * SLA + BHC * SLC) / (SLA+SLC)