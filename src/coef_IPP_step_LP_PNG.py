''' MRVC/coef_IPP_step_LP_PNG.py '''

import coef_IPP_step_LP
import os

def encode(video, n_frames, q_step):
    coef_IPP_step_LP.encode(video, n_frames, q_step)

def compute_br(video, FPS, frame_shape, n_frames, n_levels):
    frame_height = frame_shape[0]
    frame_width = frame_shape[1]
    n_channels = frame_shape[2]
    sequence_time = n_frames/FPS
    print(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")

    '''
    n_total_bytes = 0
    for k in range(0, n_frames):
        for r in range(1, n_levels):
            fn = f"{video}{r}_{k:03d}H.png"
            n_bytes = os.path.getsize(fn)
            print(fn, n_bytes)
            n_total_bytes += n_bytes
        fn = f"{video}{n_levels}_{k:03d}LL.png"
        n_bytes = os.path.getsize(fn)
        print(fn, n_bytes)
        n_total_bytes += n_bytes
        fn = f"{video}{n_levels}_{k:03d}H.png"
        n_bytes = os.path.getsize(fn)
        print(fn, n_bytes)
        n_total_bytes += n_bytes
    '''

    command = f"cat {video}{n_levels}_???LL.png | gzip -9 > /tmp/coef_IPP_step_{n_levels}_LL.gz"
    print(command)
    os.system(command)
    n_total_bytes = os.path.getsize(f"/tmp/coef_IPP_step_{n_levels}_LL.gz")
    #n_total_bytes = os.path.getsize(f"/tmp/coef_IPP_step_{n_levels}_LL.gz")
    print(f"LL{n_levels}: {n_total_bytes}")

    for r in range(1, n_levels+1):
        command = f"cat {video}{r}_???H.png | gzip -9 > /tmp/coef_IPP_step_{r}_H.gz"
        print(command)
        os.system(command)
        n_bytes = os.path.getsize(f"/tmp/coef_IPP_step_{r}_H.gz")
        n_total_bytes += n_bytes
        print(f"H{r}: {n_bytes}")

    KBPS = n_total_bytes*8/sequence_time/1000
    BPP = n_total_bytes*8/(frame_width*frame_height*n_channels*n_frames)

    return KBPS, BPP, n_total_bytes
