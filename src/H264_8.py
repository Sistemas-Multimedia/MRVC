''' MRVC/H264_8.py '''

# Only used if we work in the RGB domain and the LP.

import config
import frame
import os
import values
import debug

if config.color == "YCoCg":
    import YCoCg as YUV

if config.color == "YCrCb":
    import YCrCb as YUV

if config.color == "RGB":
    import RGB as YUV

def E(E_k, prefix, k, q_step):
    # Ojo, E_k en YCoCg viene en 16 bits?
    debug.print("Error YUV", E_k.max(), E_k.min(), q_step)
    E_k_RGB = YUV.to_RGB(E_k)
    debug.print("Error RGB", E_k_RGB.max(), E_k_RGB.min())
    #frame.write(clip(E_k_RGB+128), prefix + "before_", k)
    frame.write(E_k_RGB, prefix + "before_", k)
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
    dq_E_k = frame.read(prefix, k)
    dq_E_k = dq_E_k / 256
    dq_E_k = values.denorm(dq_E_k, max, min)
    dq_E_k = YUV.from_RGB(dq_E_k)
    return dq_E_k
