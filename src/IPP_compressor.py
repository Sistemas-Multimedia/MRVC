''' MRVC/IPP_compressor.py '''

import IPP_step
#import DWT as spatial_transform
import LP as spatial_transform
#import L_DWT as L
import L_LP as L
#import H_DWT as H
import H_LP as H
#import YCoCg as YUV
import YCrCb as YUV
#import RGB as YUV
import frame
import numpy as np
import config

gains = spatial_transform.compute_gains(config.n_levels)
print(gains)

print("Computing Spatial Transform")
for k in range(config.n_frames):
    V_k = frame.read(f"{config.input_video}{k:03d}")
    V_k = YUV.from_RGB(V_k)
    decomposition = spatial_transform.analyze(V_k, n_levels=config.n_levels)
    #print("len =", len(decomposition))
    L.write(decomposition[0], f"{config.input_video}{config.n_levels}_", k)
    for l in range(0, config.n_levels):
        H.write(decomposition[l+1], f"{config.input_video}{config.n_levels-l}_", k)

print("IPP... encoding")

print(f"Computing SRL {config.n_levels}")
delta = config.q_step*gains[0]
print("delta =", delta)
if delta < 1:
    delta = 1
IPP_step.encode(f"{config.input_video}{config.n_levels}_", f"{config.codestream}{config.n_levels}_", config.n_frames, delta)
for k in range(config.n_frames):
    reconstructed__V_k_H = L.read(f"{config.input_video}{config.n_levels}_reconstructed_H", k)
    V_k_L = L.read(f"{config.input_video}{config.n_levels}_", k)
    reconstructed_V_k_H = H.reduce(reconstructed__V_k_H)
    reconstructed_V_k = spatial_transform.synthesize_step(V_k_L, reconstructed_V_k_H)
    L.write(reconstructed_V_k, f"{config.input_video}{config.n_levels-1}_", k)

for l in range(config.n_levels-1, 0, -1):
    print(f"Computing SRL {l}")
    delta = config.q_step*gains[config.n_levels-l-1]
    print("delta =", delta)
    if delta < 1:
        delta = 1
    IPP_step.encode(f"{config.input_video}{l}_", f"{config.codestream}{l}_", config.n_frames, delta)
    for k in range(config.n_frames):
        reconstructed__V_k_H = L.read(f"{config.input_video}{l}_reconstructed_H", k)
        V_k_L = L.read(f"{config.input_video}{l}_", k)
        reconstructed_V_k_H = H.reduce(reconstructed__V_k_H)
        reconstructed_V_k = spatial_transform.synthesize_step(V_k_L, reconstructed_V_k_H)
        L.write(reconstructed_V_k, f"{config.input_video}{l-1}_", k)

for l in range(config.n_levels, -1, -1):
    for k in range(config.n_frames):
        V_k = L.read(f"{config.input_video}{l}_", k)
        V_k = YUV.to_RGB(V_k)
        V_k = np.clip(V_k, 0, 255).astype(np.uint8)
        frame.write(V_k, f"{config.output_video}{l}_{k:03d}")

config._print()

