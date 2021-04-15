''' MRVC/IPP_compressor.py '''

#import coef_IPP_step_PNG as IPP_step
import coef_IPP_step_H264 as IPP_step
import DWT as spatial_transform
#import LP as spatial_transform
import L_DWT as L
#import L_LP as L
import H_DWT as H
#import H_LP as H
#import YCoCg as YUV
#import YCrCb as YUV
import RGB as YUV
import frame
import numpy as np
import deadzone as Q
import distortion

video = "/tmp/original_"
n_levels = 3
n_frames = 30
FPS = 30

q_min = 31
q_max = 41

gains = spatial_transform.compute_gains(n_levels)
print(gains)

print("Computing spatial transform ...")
for k in range(n_frames):
    V_k = frame.read(video, k)
    V_k = YUV.from_RGB(V_k)
    decomposition = spatial_transform.analyze(V_k, n_levels=n_levels)
    #print("len =", len(decomposition))
    L.write(decomposition[0], f"{video}{n_levels}_", k)
    for l in range(0, n_levels):
        H.write(decomposition[l+1], f"{video}{n_levels-l}_", k)

print("Performing IPP... encoding")

print(f"Computing SRL {n_levels}")
#delta = q_step/gains[0]
#delta = q_step/gains[n_levels-1]
delta = q_min
#print("delta =", delta)
if delta < 1:
    delta = 1
IPP_step.encode(f"{video}{n_levels}_", n_frames, delta)
for k in range(n_frames):
    reconstructed__V_k_H = L.read(f"{video}{n_levels}_reconstructed_H", k)
    V_k_L = L.read(f"{video}{n_levels}_", k)
    reconstructed_V_k_H = H.reduce(reconstructed__V_k_H)
    reconstructed_V_k = spatial_transform.synthesize_step(V_k_L, reconstructed_V_k_H)
    L.write(reconstructed_V_k, f"{video}{n_levels-1}_", k)

for l in range(n_levels-1, 0, -1):
    print(f"Computing SRL {l}")
    #delta = q_step/gains[n_levels-l-1]
    #delta = q_step/gains[l]
    delta = q_min + (q_max-q_min)*n_levels/(l+3)
    print("delta =", delta)
    if delta < 1:
        delta = 1
    IPP_step.encode(f"{video}{l}_", n_frames, delta)
    for k in range(n_frames):
        reconstructed__V_k_H = L.read(f"{video}{l}_reconstructed_H", k)
        V_k_L = L.read(f"{video}{l}_", k)
        reconstructed_V_k_H = H.reduce(reconstructed__V_k_H)
        reconstructed_V_k = spatial_transform.synthesize_step(V_k_L, reconstructed_V_k_H)
        L.write(reconstructed_V_k, f"{video}{l-1}_", k)

for l in range(n_levels, -1, -1):
    for k in range(n_frames):
        V_k = L.read(f"{video}{l}_", k)
        V_k = YUV.to_RGB(V_k)
        V_k = np.clip(V_k, 0, 255).astype(np.uint8)
        frame.write(V_k, f"{video}{l}_reconstructed_", k)

KBPS, BPP, N_bytes = IPP_step.compute_br(video, FPS,
                                         frame.get_frame_shape(video), n_frames, n_levels)

_distortion = distortion.AMSE(video, f"{video}0_reconstructed_", n_frames)

print("Q_step:", q_min, "BPP:", BPP, "KBPS:", KBPS, "Average AMSE:", _distortion, "N_bytes:", N_bytes)
