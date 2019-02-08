
from MC.optical.motion import motion_estimation
from MC.optical.motion import estimate_frame

def calcula_prediction():
    ELA = BL - BLA
    ELC = BL - BLC
    '''Modificación para corregir la división por 0'''
    SLA = 1 / (1+abs(ELA))
    SLC = 1 / (1+abs(ELC))
         
    prediction_BH = (BHA*SLA + BHC*SLC)/(SLA + SLC)
    return prediction_BH