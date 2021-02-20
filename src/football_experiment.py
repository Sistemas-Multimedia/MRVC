''' MRVC/stockholm_experiment.py '''

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

print("Computing DWT")
for k in range(n_frames):
    V_k = frame.read(input_video, k)
    V_k = YCoCg.from_RGB(V_k)
    V_k_L, V_k_H = DWT.analyze_step(V_k) # (a)
    L.write(V_k_L, input_video, k) # (g) L.write(V_k_L, input_video + "L", k)
    H.write(V_k_H, input_video, k) #H.write(V_k_H, input_video + "H", k)

print("IPP... encoding")
#IPP_step.encode(input_video + "L", input_video + "H", codestream, n_frames, q_step)
IPP_step.encode(input_video, codestream, n_frames, q_step)

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
