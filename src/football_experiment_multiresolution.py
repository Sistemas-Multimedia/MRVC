''' MRVC/stockholm_experiment_multiresolution.py '''

import IPP_step
import DWT
import YCoCg
import frame
import L
import H
import numpy as np

q_step = 128
n_frames = 128
input_video = "/tmp/football_"
codestream = "/tmp/football_codestream_"
output_video = "/tmp/football_decoded_"
levels = 3

print("Computing DWT")
for k in range(n_frames):
    V_k = frame.read(input_video, k)
    V_k = YCoCg.from_RGB(V_k)
    decomposition = DWT.analyze(V_k, levels=levels)
    L.write(decomposition[0], input_video + "L" + str(l), k)
    for l in range(levels):
        H.write(decomposition[l+1], input_video + "H" + str(l), k)

print("IPP... encoding")
IPP_step.encode(input_video + "L" + str(levels), input_video + "H" + str(levels), codestream, n_frames, q_step)
for k in range(n_frames):
    reconstruction_V_k_H = frame.read(codestream + "reconstructed_H", k)
    V_k_L = frame.read(input_video + "L" + str(levels), k)
    reduced_reconstruction_V_k_H = H.reduce(reconstruction_V_k_H)
    reconstruction_V_k = DWT.synthesize_step(V_k_L, reduced_reconstruction_V_k_H)
    frame.write(reconstruction_V_k, codestream + "reconstructed", k)
for l in range(levels,1,-1):
    IPP_step.encode(codestream + "reconstructed" + str(l), input_video + "H" + str(l), codestream, n_frames, q_step)

#n_frames = 16
#encoder = IPP_step.Encoder(video="/tmp/football_", codestream="/tmp/football_codestream_", q_step=128)
#for k in range(1, n_frames):
#    encoder.encode_next_frame()

print("IPP ... Decoding")
IPP_step.decode(codestream, output_video, n_frames, q_step)

for k in range(n_frames):
    V_k = frame.read(output_video, k)
    V_k = YCoCg.to_RGB(V_k)
    V_k = np.clip(V_k, 0, 255)
    frame.write(V_k, output_video + "R_", k)
