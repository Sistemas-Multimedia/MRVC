''' MRVC/imae_IPP_compressor.py '''

import image_IPP_step as IPP_step
import DWT as spatial_transform
#import LP as spatial_transform
import L_DWT as L
#import L_LP as L
import H_DWT as H
#import H_LP as H
#import YCoCg as YUV
import YCrCb as YUV
#import RGB as YUV
import frame
import numpy as np
import deadzone as Q
import config


print("IPP... encoding")

delta = Q.step
print("delta =", delta)

IPP_step.encode(f"{config.input_video}", f"{config.codestream}", config.n_frames, delta)


