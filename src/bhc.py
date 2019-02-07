from MC.optical.motion import generate_prediction


def do_something(AL, BL, AH, CL,CH):
    BHA = generate_prediction(AL, BL, AH)
    BHC = generate_prediction(CL, BL, CH)
    BLA = generate_prediction(AL, BL, AL)
    BLC = generate_prediction(CL, BL, CL)
    ELA = BL - BLA
    ELC = BL - BLC
    SAL=1/( 1+ ELA)
    SCL = 1 / (1 + ELC)
    prediction_BH = ((BHA * SAL) + (BHC * SCL)) / (SAL + SCL)
    return prediction_BH
