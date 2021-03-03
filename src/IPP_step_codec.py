''' MRVC/stockholm_experiment.py '''

import IPP_step
#import DWT as spatial_transform
import LP as spatial_transform
import YCoCg as YUV
import frame
#import L_DWT as L
import L_LP as L
#import H_DWT as H
import H_LP as H
import numpy as np
import config

print("Computing Spatial Transform")
for k in range(config.n_frames):
    V_k = frame.read(f"{config.input_video}{k:03d}")
    V_k = YUV.from_RGB(V_k)
    V_k_L, V_k_H = spatial_transform.analyze_step(V_k) # (a)
    L.write(V_k_L, config.input_video, k) # (g) L.write(V_k_L, input_video + "L", k)
    H.write(V_k_H, config.input_video, k) #H.write(V_k_H, input_video + "H", k)

print("IPP... encoding")
IPP_step.encode(config.input_video, config.codestream, config.n_frames, config.q_step)

print("IPP ... Decoding")
IPP_step.decode(config.codestream, config.output_video, config.n_frames, config.q_step)

for k in range(config.n_frames):
    V_k = frame.read(f"{config.output_video}{k:03d}")
    V_k = YUV.to_RGB(V_k)
    V_k = np.clip(V_k, 0, 255).astype(np.uint8)
    frame.write(V_k, f"{config.output_video}R_{k:03d}")
