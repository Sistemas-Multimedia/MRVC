''' MRVC/stockholm_experiment.py '''

import IPP_step
import DWT as spatial_transform
#import LP as spatial_transform
import YCoCg as YUV
import frame
import L_DWT as L
#import L_LP as L
import H_DWT as H
#import H_LP as H
import numpy as np

video = "/tmp/original_"
n_frames = 30
q_step = 16

print("Computing Spatial Transform")
for k in range(n_frames):
    V_k = frame.read(video, k)
    V_k = YUV.from_RGB(V_k)
    V_k_L, V_k_H = spatial_transform.analyze_step(V_k) # (a)
    L.write(V_k_L, video, k) # (g) L.write(V_k_L, input_video + "L", k)
    H.write(V_k_H, video, k) #H.write(V_k_H, input_video + "H", k)

print("IPP... encoding")
IPP_step.encode(video, n_frames, q_step)

print("IPP ... Decoding")
IPP_step.decode(video, n_frames, q_step)

for k in range(n_frames):
    V_k = frame.read(video, k)
    V_k = YUV.to_RGB(V_k)
    V_k = np.clip(V_k, 0, 255).astype(np.uint8)
    frame.write(V_k, f"{video}reconstructed_", k)
