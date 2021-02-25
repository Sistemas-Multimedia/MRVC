''' MRVC/stockholm_experiment_multiresolution.py '''

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
    decomposition = DWT.analyze(V_k, n_levels=config.n_levels)
    #print("len =", len(decomposition))
    L.write(decomposition[0], f"{config.input_video}{config.n_levels}_", k)
    for l in range(0, config.n_levels):
        H.write(decomposition[l+1], f"{config.input_video}{config.n_levels-l}_", k)

print("IPP... encoding")

print(f"Computing SRL {config.n_levels}")
IPP_step.encode(f"{config.input_video}{config.n_levels}_", f"{config.codestream}{config.n_levels}_", config.n_frames, config.q_step)
for k in range(config.n_frames):
    reconstructed__V_k_H = L.read(f"{config.input_video}{config.n_levels}_reconstructed_H", k)
    V_k_L = L.read(f"{config.input_video}{config.n_levels}_", k)
    reconstructed_V_k_H = H.reduce(reconstructed__V_k_H)
    reconstructed_V_k = DWT.synthesize_step(V_k_L, reconstructed_V_k_H)
    L.write(reconstructed_V_k, f"{config.input_video}{config.n_levels-1}_", k)

for l in range(config.n_levels-1, 0, -1):
    print(f"Computing SRL {l}")
    IPP_step.encode(f"{config.input_video}{l}_", f"{config.codestream}{l}_", config.n_frames, config.q_step)
    for k in range(config.n_frames):
        reconstructed__V_k_H = L.read(f"{config.input_video}{l}_reconstructed_H", k)
        V_k_L = L.read(f"{config.input_video}{l}_", k)
        reconstructed_V_k_H = H.reduce(reconstructed__V_k_H)
        reconstructed_V_k = DWT.synthesize_step(V_k_L, reconstructed_V_k_H)
        L.write(reconstructed_V_k, f"{config.input_video}{l-1}_", k)

for l in range(config.n_levels, -1, -1):
    for k in range(config.n_frames):
        V_k = L.read(f"{config.input_video}{l}_", k)
        V_k = YCoCg.to_RGB(V_k)
        V_k = np.clip(V_k, 0, 255).astype(np.uint8)
        frame.write(V_k, f"{config.output_video}{l}_{k:03d}")
