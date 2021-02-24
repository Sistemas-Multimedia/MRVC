''' MRVC/stockholm_experiment_multiresolution.py '''

import IPP_step
import DWT
import YCoCg
import frame
import L
import H
import numpy as np

q_step = 12800
n_frames = 32
input_video = "/tmp/football_"
codestream = "/tmp/football_codestream_"
output_video = "/tmp/football_decoded_"
levels = 3

print("Computing DWT")
for k in range(n_frames):
    V_k = frame.read(f"{input_video}{k:03d}")
    V_k = YCoCg.from_RGB(V_k)
    decomposition = DWT.analyze(V_k, n_levels=levels)
    print("len =", len(decomposition))
    L.write(decomposition[0], f"{input_video}{levels}_", k)
    for l in range(0, levels):
        H.write(decomposition[l+1], f"{input_video}{levels-l}_", k)
#quit()
print("IPP... encoding")

print(f"Computing SRL {levels}")
IPP_step.encode(f"{input_video}{levels}_", f"{codestream}{levels}_", n_frames, q_step)
for k in range(n_frames):
    #reconstructed__V_k_H = frame.read(f"{input_video}{levels}_reconstructed_H", k)
    reconstructed__V_k_H = L.read(f"{input_video}{levels}_reconstructed_H", k)
    #print(reconstructed__V_k_H.dtype)
    V_k_L = L.read(f"{input_video}{levels}_", k)
    #print(V_k_L.dtype)
    #print(reconstructed__V_k_H.max(), reconstructed__V_k_H.min(), V_k_L.max(), V_k_L.min())
    reconstructed_V_k_H = H.reduce(reconstructed__V_k_H)
    reconstructed_V_k = DWT.synthesize_step(V_k_L, reconstructed_V_k_H)
    #print(reconstructed_V_k.max(), reconstructed_V_k.min())
    #frame.write(reconstructed_V_k, f"{input_video}{levels}_reconstructed_LL", k)
    #frame.write(reconstructed_V_k, f"{input_video}{levels-1}_LL", k)
    L.write(reconstructed_V_k, f"{input_video}{levels-1}_", k)

for l in range(levels-1, 0, -1):
    print(f"Computing SRL {l}")
    #IPP_step.encode(f"{input_video}{l}_reconstructed_", f"{codestream}{l}_", n_frames, q_step)
    IPP_step.encode(f"{input_video}{l}_", f"{codestream}{l}_", n_frames, q_step)
    for k in range(n_frames):
        #reconstructed__V_k_H = frame.read(f"{input_video}{l}_reconstructed_H", k)
        reconstructed__V_k_H = L.read(f"{input_video}{l}_reconstructed_H", k)
        V_k_L = L.read(f"{input_video}{l}_", k)
        reconstructed_V_k_H = H.reduce(reconstructed__V_k_H)
        reconstructed_V_k = DWT.synthesize_step(V_k_L, reconstructed_V_k_H)
        print(reconstructed_V_k.max())
        #frame.write(reconstructed_V_k, f"{input_video}{l}_reconstructed_LL", k)
        #frame.write(reconstructed_V_k, f"{input_video}{l-1}_LL", k)
        L.write(reconstructed_V_k, f"{input_video}{l-1}_", k)
#quit()
for l in range(levels, -1, -1):
    for k in range(n_frames):
        V_k = L.read(f"{input_video}{l}_", k)
        V_k = YCoCg.to_RGB(V_k)
        V_k = np.clip(V_k, 0, 255).astype(np.uint8)
        frame.write(V_k, f"{input_video}{l}_R_{k:03d}")
