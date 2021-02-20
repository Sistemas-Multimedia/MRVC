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
    L.write(decomposition[0], f"{input_video}_L{levels}", k)
    for l in range(levels, 1, -1):
        H.write(decomposition[l-1], f"{input_video}_H{l}", k)

print("IPP... encoding")

print(f"Computing SRL {levels}")
IPP_step.encode(f"{input_video}_L{levels}", f"{input_video}_H{levels}", codestream, n_frames, q_step)
for k in range(n_frames):
    reconstruction__V_k_H = frame.read(f"{codestream}_reconstructed_H", k)
    V_k_L = L.read(f"{input_video}_L{levels}", k)
    reconstruction_V_k_H = H.reduce(reconstruction__V_k_H)
    reconstruction_V_k = DWT.synthesize_step(V_k_L, reconstruction_V_k_H)
    frame.write(reconstruction_V_k, f"{input_video}_reconstructed_L{levels}", k)

for l in range(levels, 1, -1):
    print(f"Computing SRL {l+1}")
    IPP_step.encode(f"{input_video}_reconstructed_L{l}", f"{input_video}_H{l}", codestream, n_frames, q_step)
    for k in range(n_frames):
        reconstruction__V_k_H = frame.read(f"{codestream}_reconstructed_H", k)
        V_k_L = frame.read(f"{input_video}L{l}", k)
        reconstruction_V_k_H = H.reduce(reconstruction__V_k_H)
        reconstruction_V_k = DWT.synthesize_step(V_k_L, reconstruction_V_k_H)
        frame.write(reconstruction_V_k, f"{input_video}_reconstructed_L{l}", k)

