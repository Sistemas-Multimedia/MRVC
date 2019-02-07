from MC.optical.motion import generate_prediction


def do_something(AL, BL, AH, CL,  CH):
    BHA = generate_prediction(AL, BL, AH)	        
    BHC = generate_prediction(CL, BL, CH)
    prediction_BH = (BHA + BHC) / 2
    return prediction_BH
