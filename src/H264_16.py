''' MRVC/H264_16.py '''

import config
import frame
import os
import values
import debug
import values
import numpy as np

if config.color == "YCoCg":
    import YCoCg as YUV

if config.color == "YCrCb":
    import YCrCb as YUV

if config.color == "RGB":
    import RGB as YUV

def _E(E_k, prefix, k, q_step):
    debug.print("Error YUV", E_k.max(), E_k.min(), q_step)
    E_k_RGB = YUV.to_RGB(E_k)
    debug.print("Error RGB", E_k_RGB.max(), E_k_RGB.min())
    #frame.write(clip(E_k_RGB+128), prefix + "before_", k)
    norm_E_k_RGB, max, min = values.normalize(E_k_RGB)
    norm_E_k_RGB *= 255
    debug.print("Error normalized", norm_E_k_RGB.max(), norm_E_k_RGB.min())
    frame.write(norm_E_k_RGB, prefix + "before_", k)
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
    #os.system(f"ffmpeg -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
    dq_E_k = frame.read(prefix, k)
    debug.print("Error RGB after H264", dq_E_k.max(), dq_E_k.min())
    dq_E_k = dq_E_k / 255
    dq_E_k = values.denormalize(dq_E_k, max, min)
    debug.print("Error de-normalized RGB", dq_E_k.max(), dq_E_k.min())
    dq_E_k = YUV.from_RGB(dq_E_k)
    debug.print("Error de-normalized YUV", dq_E_k.max(), dq_E_k.min())
    return dq_E_k

# Idéntico al de arriba, pero usando 10 bits en H264. El rendimiento es muy parecido.
def E(E_k, prefix, k, q_step):
    debug.print("Error YUV", E_k.max(), E_k.min(), q_step)
    E_k_RGB = YUV.to_RGB(E_k)
    debug.print("Error RGB", E_k_RGB.max(), E_k_RGB.min())
    E_k_RGB_normalized, max, min = values.normalize(E_k_RGB)
    #E_k_RGB_normalized *= 1024
    E_k_RGB_normalized *= 65535
    E_k_RGB_normalized = np.round(E_k_RGB_normalized).astype(np.uint16)
    debug.print("Error normalized", E_k_RGB_normalized.max(), E_k_RGB_normalized.min())
    frame.write(E_k_RGB_normalized, prefix + "before_", k)
    #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -pix_fmt yuv420p10le -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
    os.system(f"ffmpeg -y -i {prefix}before_{k:03d}.png -pix_fmt yuv420p10le -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")    
    #os.system(f"ffmpeg -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
    dq_E_k = frame.read(prefix, k)
    debug.print("Error RGB after H264", dq_E_k.max(), dq_E_k.min())
    #dq_E_k = dq_E_k / 1024
    dq_E_k = dq_E_k / 65535
    dq_E_k = values.denormalize(dq_E_k, max, min)
    debug.print("Error de-normalized RGB", dq_E_k.max(), dq_E_k.min())
    dq_E_k = YUV.from_RGB(dq_E_k)
    debug.print("Error de-normalized YUV", dq_E_k.max(), dq_E_k.min())
    return dq_E_k

def E1(E_k, prefix, k, q_step):
    print("Error YUV", E_k.max(), E_k.min())
    E_k_RGB = YUV.to_RGB(E_k) + 128
    print("Error RGB", E_k_RGB.max(), E_k_RGB.min())
    #frame.write(clip(E_k_RGB+128), prefix + "before_", k)
    #norm_E_k_RGB = norm(E_k_RGB)
    #print("Error norm RGB", norm_E_k_RGB.max(), norm_E_k_RGB.min())
    frame.write(E_k_RGB, prefix + "before_", k)
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
    dq_E_k = (YUV.from_RGB(frame.read(prefix, k)-128))
    return dq_E_k

# See ffmpeg -h encoder=libx264
def E2(E_k, prefix, k, q_step):
    debug.print("Error YUV", E_k.max(), E_k.min(), q_step)
    E_k_RGB = YUV.to_RGB(E_k)
    debug.print("Error RGB", E_k_RGB.max(), E_k_RGB.min())
    E_k_RGB_clipped = np.round(values.clip(E_k_RGB + 512, 0, 1024)).astype(np.uint16)
    debug.print("Error clipped", E_k_RGB_clipped.max(), E_k_RGB_clipped.min())
    frame.write(E_k_RGB_clipped, prefix + "before_", k)
    #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -pix_fmt yuv420p10le -profile high10 -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
    os.system(f"ffmpeg -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
    dq_E_k = frame.read(prefix, k) - 512
    debug.print("Error RGB after H264", dq_E_k.max(), dq_E_k.min())
    dq_E_k = YUV.from_RGB(dq_E_k)
    debug.print("Error YUV after RGB", dq_E_k.max(), dq_E_k.min())
    return dq_E_k
