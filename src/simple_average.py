<<<<<<< HEAD
from MC.optical.motion import motion_estimation
from MC.optical.motion import estimate_frame
import sys
=======
#from MC.optical.motion import motion_estimation
#from MC.optical.motion import estimate_frame
#from DWT import DWT
>>>>>>> 997e5f8cb643efdbb339c89c28e501eb04fff808

def generate_prediction(aL, bL, cL, AH, CH):
    flow_AL_BL = motion_estimation(aL, bL)
    flow_CL_BL = motion_estimation(cL, bL)
    flow_AL_BL = DWT.backward((flow_AL_BL, [None, None, None]))
    flow_CL_BL = DWT.backward((flow_CL_BL, [None, None, None]))
    BAH = estimate_frame(AH, flow_AL_BL)
    BCH = estimate_frame(CH, flow_CL_BL)
    return (BAH + BCH) / 2

