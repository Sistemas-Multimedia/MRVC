''' MRVC/coef_IPP_step_LP_H264.py '''

import config

if config.color == "YCoCg":
    import YCoCg as YUV

if config.color == "YCrCb":
    import YCrCb as YUV

if config.color == "RGB":
    import RGB as YUV

import coef_IPP_step
import os
import L_LP as L
import frame

def encode(video, n_frames, q_step):
    coef_IPP_step.encode(video, n_frames, q_step)

def compute_br(video, FPS, frame_shape, n_frames, n_levels):
    frame_height = frame_shape[0]
    frame_width = frame_shape[1]
    n_channels = frame_shape[2]
    sequence_time = n_frames/FPS
    print(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")

    # LL subband
    for k in range(n_frames):
        V_k = L.read(f"{video}{n_levels}_", k)
        V_k_RGB = YUV.to_RGB(V_k)
        frame.write(V_k_RGB, f"{video}{n_levels}_LL_8bpp_", k)
    command = f"ffmpeg -loglevel fatal -y -i {video}{n_levels}_LL_8bpp_%03d.png -crf 0 /tmp/coef_IPP_step_{n_levels}_LL.mp4"
    #command = f"cat {video}{n_levels}_???LL.png | gzip -9 > /tmp/coef_IPP_step_{n_levels}_LL.gz"
    print(command)
    os.system(command)
    n_total_bytes = os.path.getsize(f"/tmp/coef_IPP_step_{n_levels}_LL.mp4")
    #n_total_bytes = os.path.getsize(f"/tmp/coef_IPP_step_{n_levels}_LL.gz")
    print(f"LL{n_levels}: {n_total_bytes}")
    
    # H subbands
    for r in range(1, n_levels+1):
        #command = f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {video}{r}*.mp4; do echo \"file '$f'\"; done) -c copy /tmp/coef_IPP_step_{r}_H.mp4"
        command = f"cat {video}{r}*.mp4 | gzip -9 > /tmp/coef_IPP_step_{r}_H.gz"
        print(command)
        os.system(command)
        #n_bytes = os.path.getsize(f"/tmp/coef_IPP_step_{r}_H.mp4")
        n_bytes = os.path.getsize(f"/tmp/coef_IPP_step_{r}_H.gz")
        n_total_bytes += n_bytes
        print(f"H{r}: {n_bytes}")

    KBPS = n_total_bytes*8/sequence_time/1000
    BPP = n_total_bytes*8/(frame_width*frame_height*n_channels*n_frames)

    return KBPS, BPP, n_total_bytes
