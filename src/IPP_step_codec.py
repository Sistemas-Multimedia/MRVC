''' MRVC/stockholm_experiment.py '''

import IPP_step
import DWT
import YCoCg
import frame
import L
import H
import numpy as np
import config

print("Computing DWT")
for k in range(config.n_frames):
    V_k = frame.read(f"{config.input_video}{k:03d}")
    V_k = YCoCg.from_RGB(V_k)
    V_k_L, V_k_H = DWT.analyze_step(V_k) # (a)
    L.write(V_k_L, config.input_video, k) # (g) L.write(V_k_L, input_video + "L", k)
    H.write(V_k_H, config.input_video, k) #H.write(V_k_H, input_video + "H", k)

print("IPP... encoding")
IPP_step.encode(config.input_video, config.codestream, config.n_frames, config.q_step)

print("IPP ... Decoding")
IPP_step.decode(config.codestream, config.output_video, config.n_frames, config.q_step)

for k in range(config.n_frames):
    V_k = frame.read(f"{config.output_video}{k:03d}")
    V_k = YCoCg.to_RGB(V_k)
    V_k = np.clip(V_k, 0, 255).astype(np.uint8)
    frame.write(V_k, f"{config.output_video}R_{k:03d}")
