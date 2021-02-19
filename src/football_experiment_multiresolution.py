''' MRVC/stockholm_experiment_multiresolution.py '''

import IPP_step
import DWT
import YCoCg
import frame
import L
import H
import numpy as np

q_step = 128
n_frames = 16
input_video = "/tmp/football_"
codestream = "/tmp/football_codestream_"
output_video = "/tmp/football_decoded_"
levels = 2

print("Computing DWT")
for k in range(n_frames):
    V_k = frame.read(input_video, k)
    V_k = YCoCg.from_RGB(V_k)
    decomposition = DWT.analyze(V_k, levels=levels)
    L.write(decomposition[0], input_video + f"L{levels}", k)
    for l in range(levels, 1, -1):
        H.write(decomposition[l-1], input_video + f"H{l}", k)

print("IPP... encoding")

print(f"Computing SRL {levels}")
IPP_step.encode(input_video + "L" + str(levels), input_video + "H" + str(levels), codestream, n_frames, q_step)
for k in range(n_frames):
    reconstruction__V_k_H = frame.read(codestream + "reconstructed_H", k)
    V_k_L = frame.read(input_video + f"L{levels}", k)
    reconstruction_V_k_H = H.reduce(reconstruction__V_k_H)
    reconstruction_V_k = DWT.synthesize_step(V_k_L, reconstruction_V_k_H)
    frame.write(reconstruction_V_k, codestream + f"reconstructed{levels}_", k)

for l in range(levels,1,-1):
    print(f"Computing SRL {l+1}")
    IPP_step.encode(codestream + f"reconstructed{l}" + "_", input_video + f"H{l}", codestream, n_frames, q_step)
    for k in range(n_frames):
        reconstruction__V_k_H = frame.read(codestream + "reconstructed_H", k)
        V_k_L = frame.read(input_video + f"L{l}", k)
        reconstruction_V_k_H = H.reduce(reconstruction__V_k_H)
        reconstruction_V_k = DWT.synthesize_step(V_k_L, reconstruction_V_k_H)
        frame.write(reconstruction_V_k, codestream + f"reconstructed{l}_", k)

