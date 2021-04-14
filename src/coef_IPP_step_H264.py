''' MRVC/coef_IPP_step_H264.py '''

import numpy as np
import DWT as spatial_transform
#import LP as spatial_transform
import L_DWT as L
#import L_LP as L
import H_DWT as H
#import H_LP as H
#import deadzone as Q
import YCoCg as YUV
import motion
import frame
import colors
import cv2
import os

def norm(x):
    max = x.max()
    min = x.min()
    return (x-min)/(max-min), max, min
    #return (frame.normalize(x)*255).astype(np.uint8)

def denorm(x, max, min):
    return x*(max-min)+min
    
def clip(x):
    return(np.clip(x+128, 0 ,255).astype(np.uint8))

def E_codec2(E_k, prefix, k, q_step):
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

def E_codec(E_k, prefix, k, q_step):
    print("Error YUV", E_k.max(), E_k.min(), q_step)
    E_k_RGB = YUV.to_RGB(E_k)
    print("Error RGB", E_k_RGB.max(), E_k_RGB.min())
    #frame.write(clip(E_k_RGB+128), prefix + "before_", k)
    norm_E_k_RGB, max, min = norm(E_k_RGB)
    norm_E_k_RGB *= 256
    print("Error norm RGB", norm_E_k_RGB.max(), norm_E_k_RGB.min())
    frame.write(norm_E_k_RGB, prefix + "before_", k)
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
    dq_E_k = frame.read(prefix, k)
    dq_E_k = dq_E_k / 256
    dq_E_k = denorm(dq_E_k, max, min)
    dq_E_k = YUV.from_RGB(dq_E_k)
    return dq_E_k

def encode(video, n_frames, q_step):
    try:
        k = 0
        V_k_L = L.read(video, k)
        V_k_H = H.read(video, k, V_k_L.shape)
        #L.write(V_k_L, video, k) # (g)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        initial_flow = np.zeros((_V_k_L.shape[0], _V_k_L.shape[1], 2), dtype=np.float32)
        _V_k_1_L = _V_k_L # (E.b)
        _V_k_H = H.interpolate(V_k_H) # (b)
        _E_k_H = _V_k_H # (c)
        #quantized__E_k_H = Q.quantize(_E_k_H, step=q_step) # (d)
        #dequantized__E_k_H = Q.dequantize(quantized__E_k_H, step=q_step) # (E.g)
        dequantized__E_k_H = E_codec(_E_k_H, video, 0, q_step)
        reconstructed__V_k_H = dequantized__E_k_H # (E.h)
        L.write(reconstructed__V_k_H, video + "reconstructed_H", k)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        #quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
        #H.write(quantized_E_k_H, video, k) # (g)
        for k in range(1, n_frames):
            V_k_L = L.read(video, k)#V_k_L = L.read(L_sequence, k)
            V_k_H = H.read(video, k, V_k_L.shape)#V_k_H = H.read(H_sequence, k)
            _V_k_L = L.interpolate(V_k_L) # (E.a)
            flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0], initial_flow) # (E.c)
            prediction__V_k_L = motion.make_prediction(_V_k_1_L, flow) # (E.d)
            frame.debug_write(norm(prediction__V_k_L)[0], f"{video}encoder_prediction_L_", k)
            _V_k_1_L = _V_k_L # (E.b)
            _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
            frame.debug_write(norm(_V_k_L)[0], f"{video}encoder_predicted_L_", k)
            frame.debug_write(clip(_E_k_L), f"{video}encoder_prediction_error_L_", k)
            S_k = abs(_E_k_L[:,:,0]) < abs(_V_k_L[:,:,0] - np.average(_V_k_L[:,:,0])) # (E.f)
            if __debug__:
                # If S_k[i,j] is True, then the coef is P-type,
                # otherwise I-type.
                unique, counts = np.unique(S_k, return_counts=True)
                histogram = dict(zip(unique, counts))
                if True in histogram:
                    histogram['P'] = histogram.pop(True)
                if False in histogram:
                    histogram['I'] = histogram.pop(False)
                print("Coefs type histogram:", histogram)
            frame.debug_write(cv2.merge((S_k.astype(np.uint8),S_k.astype(np.uint8),S_k.astype(np.uint8))), f"{video}encoder_selection_", k)
            _V_k_H = H.interpolate(V_k_H) # (b)
            frame.debug_write(clip(_V_k_H), f"{video}encoder_predicted_H_", k)
            prediction__V_k_H = motion.make_prediction(reconstructed__V_k_1_H, flow) # (E.j)
            frame.debug_write(clip(prediction__V_k_H), f"{video}encoder_prediction_H_", k)
            IP_prediction__V_k_H = np.empty_like(prediction__V_k_H)
            for c in range(3):
                IP_prediction__V_k_H[:,:,c] = np.where(S_k, 0, prediction__V_k_H[:,:,c]) # (E.k) Remember that we are working with coefs with 0 average.
            frame.debug_write(clip(IP_prediction__V_k_H), f"{video}encoder_IP_prediction_H_", k)
            _E_k_H = _V_k_H - IP_prediction__V_k_H[:_V_k_H.shape[0], :_V_k_H.shape[1], :] # (c)
            frame.debug_write(clip(_E_k_H), f"{video}encoder_prediction_error_H_", k)
            #quantized__E_k_H = Q.quantize(_E_k_H, step=q_step) # (d)
            #dequantized__E_k_H = Q.dequantize(quantized__E_k_H, step=q_step) # (E.g)
            dequantized__E_k_H = E_codec(_E_k_H, video, k, q_step)
            frame.debug_write(clip(dequantized__E_k_H), f"{video}encoder_dequantized_prediction_error_H_", k)
            reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H[:dequantized__E_k_H.shape[0], :dequantized__E_k_H.shape[1], :] # (E.h)
            L.write(reconstructed__V_k_H, video + "reconstructed_H", k)
            frame.debug_write(clip(reconstructed__V_k_H), f"{video}encoder_reconstructed_", k)
            reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
            #quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
            #L.write(V_k_L, video, k) # (g)
            #H.write(quantized_E_k_H, video, k) # (g)
    except:
        print(colors.red(f'IPP_step.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
        raise

def compute_br(video, FPS, frame_shape, n_frames, n_levels):
    frame_height = frame_shape[0]
    frame_width = frame_shape[1]
    n_channels = frame_shape[2]
    sequence_time = n_frames/FPS
    print(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")

    # LL subband
    command = f"ffmpeg -loglevel fatal -y -i {video}{n_levels}_%03d.png -crf 0 /tmp/coef_IPP_step_{n_levels}_LL.mp4"
    print(command)
    os.system(command)
    n_total_bytes = os.path.getsize(f"/tmp/coef_IPP_step_{n_levels}_LL.mp4")
    
    # H subbands
    for r in range(1, n_levels):
        command = f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {video}{r}*.mp4; do echo \"file '$f'\"; done) -c copy /tmp/coef_IPP_step_{r}_H.mp4"
        print(command)
        os.system(command)
        n_total_bytes += os.path.getsize(f"/tmp/coef_IPP_step_{r}_H.mp4")

    KBPS = n_total_bytes*8/sequence_time/1000
    BPP = n_total_bytes*8/(frame_width*frame_height*n_channels*n_frames)

    return KBPS, BPP, n_total_bytes
