''' MRVC/image_IPP.py '''

import DWT
import LP
import numpy as np
import L_DWT as L
import H_DWT as H
import deadzone as Q
import motion
import frame
import colors
import cv2
import YCoCg as YUV
import os
import cv2 as cv
import L_DWT as L

#subpixel_accuracy = 1

VIDEO_PREFIX = "../sequences/complete_stockholm/"
CODESTREAM_PREFIX = "/tmp/"
DECODED_VIDEO_PREFIX = "/tmp/decoder_"
#Q_STEP = 128
N_FRAMES = 16
LOG2_BLOCK_SIZE = 3 # BLOCK_SIZE = 1 << LOG2_BLOCK_SIZE
N_LEVELS = 5

def norm(x):
    return (frame.normalize(x)*255).astype(np.uint8)

def clip(x):
    return(np.clip(x, 0 ,255).astype(np.uint8))

def I_codec(E_k, prefix, k, q_step):
    print("Error", E_k.max(), E_k.min())
    frame.write(YUV.to_RGB(E_k), prefix + "_to_mp4_", k)
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}.png -crf {q_step} {prefix}_{k:03d}.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
    dq_E_k = (YUV.from_RGB(frame.read(prefix + "_from_mp4_", k)))
    return dq_E_k.astype(np.float64)

def E_codec(E_k, prefix, k, q_step):
    print("Error", E_k.max(), E_k.min())
    frame.write(clip(YUV.to_RGB(E_k)+128), prefix + "_to_mp4_", k)
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}.png -crf {q_step} {prefix}_{k:03d}.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
    dq_E_k = (YUV.from_RGB(frame.read(prefix + "_from_mp4_", k)-128))
    return dq_E_k.astype(np.float64)

def V_codec(motion, n_levels, prefix, frame_number):
    pyramid = LP.analyze(motion, n_levels)
    frame.write(pyramid[0][...,0], prefix+"_y", frame_number)
    frame.write(pyramid[0][...,1], prefix+"_x", frame_number)
    for resolution in pyramid[1:]:
        resolution[...] = 0
    reconstructed_motion = LP.synthesize(pyramid, n_levels)
    #return reconstructed_motion.astype(np.float32)
    return np.rint(reconstructed_motion).astype(np.int16)

def _V_codec(motion, n_levels, prefix, frame_number):
    return motion

def upscale(frame, n_levels):
    assert n_levels > 0
    _frame_ = L.interpolate(frame)
    for l in range(1, n_levels):
        _frame_ = L.interpolate(_frame_)
    return _frame_
def _upscale(frame, n_levels):
    assert n_levels > 0
    _frame_ = cv.pyrUp(frame)
    for l in range(1, n_levels):
        _frame_ = cv.pyrUp(_frame_)
    return _frame_
def _upscale(frame, n_levels):
    return frame

def downscale(_frame_, n_levels):
    assert n_levels > 0
    frame = L.reduce(_frame_)
    for l in range(1, n_levels):
        frame = L.reduce(frame)
    return frame
def _downscale(_frame_, n_levels):
    assert n_levels > 0
    frame = cv.pyrDown(_frame_)
    for l in range(1, n_levels):
        frame = cv.pyrDown(frame)
    return frame
def _downscale(_frame_, n_levels):
    return _frame_

def encode(video="/tmp/original_", codestream="/tmp/codestream_", n_frames=5, q_step=30, n_levels=subpixel_accuracy):
    try:
        k = 0
        W_k = frame.read(video, k)
        V_k = YUV.from_RGB(W_k) # (a)
        #V_k = W_k
        _V_k_1_ = upscale(V_k, n_levels) # (l and b)
        #_flow_ = np.zeros((_V_k_1_.shape[0], _V_k_1_.shape[1], 2), dtype=np.float32)
        E_k = V_k # (f)
        frame.debug_write(YUV.to_RGB(E_k), f"{codestream}encoder_prediction_error", k)
        #frame.debug_write(E_k, f"{codestream}encoder_prediction_error", k)
        dequantized_E_k = I_codec(E_k, codestream, 0, q_step) # (g and h)
        reconstructed_V_k = dequantized_E_k # (i)
        frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed", k) # Decoder's output
        reconstructed_V_k_1 = reconstructed_V_k # (j)
        for k in range(1, n_frames):
            W_k = frame.read(video, k)
            V_k = YUV.from_RGB(W_k) # (a)
            _V_k_ = upscale(V_k, n_levels) # (l)
            #_flow_ = motion.estimate(_V_k_[...,0], _V_k_1_[...,0], _flow_) # (c)
            _flow_ = motion.estimate(_V_k_[...,0], _V_k_1_[...,0]) # (c)
            #frame.debug_write(YUV.to_RGB(_V_k_1_), "/tmp/pre", k)
            #frame.debug_write(YUV.to_RGB(_V_k_), "/tmp/sig", k)
            #_flow_ = motion.estimate(_V_k_[...,0], _V_k_1_[...,0], _flowf_) # (c)
            print("COMPUTED flow", _flow_.max(), _flow_.min())
            _V_k_1_ = _V_k_ # (b)
            _reconstructed_flow_ = V_codec(_flow_, LOG2_BLOCK_SIZE, f"{codestream}motion", k) # (d and e)
            print("USED flow", _reconstructed_flow_.max(), _reconstructed_flow_.min())
            frame.debug_write(motion.colorize(_flow_), f"{codestream}flow", k)
            _reconstructed_V_k_1_ = upscale(reconstructed_V_k_1, n_levels) # (l)
            _prediction_V_k_ = motion.make_prediction(_reconstructed_V_k_1_, _reconstructed_flow_) # (j)
            prediction_V_k = downscale(_prediction_V_k_, n_levels) # (m)
            frame.debug_write(clip(YUV.to_RGB(prediction_V_k)), f"{codestream}encoder_prediction", k)
            frame.debug_write(clip(YUV.to_RGB(_prediction_V_k_)), f"{codestream}encoder_prediction_", k)
            E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
            frame.debug_write(clip(YUV.to_RGB(E_k)+128), f"{codestream}encoder_prediction_error", k)
            dequantized_E_k = E_codec(E_k, codestream, k, q_step) # (g and h)
            frame.debug_write(clip(YUV.to_RGB(dequantized_E_k)), f"{codestream}encoder_dequantized_prediction_error", k)
            reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1], :] # (i)
            frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed", k) # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (j)
    except:
        print(colors.red(f'image_IPP_step.encode(video="{video}", codestream="{codestream}", n_frames={n_frames}, q_step={q_step})'))
        raise

def compute_br(prefix, frames_per_second, frame_shape, n_frames):
    os.system(f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {prefix}_*.mp4; do echo \"file '$f'\"; done) -c copy /tmp/image_IPP_texture.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_motion_y_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_y.mp4")
    os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_motion_x_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_x.mp4")

    frame_height = frame_shape[0]
    frame_width = frame_shape[1]
    n_channels = frame_shape[2]
    sequence_time = n_frames/frames_per_second
    print(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")

    texture_bytes = os.path.getsize("/tmp/image_IPP_texture.mp4")
    kbps = texture_bytes*8/sequence_time/1000
    bpp = texture_bytes*8/(frame_width*frame_height*n_channels*n_frames)
    print(f"texture: {texture_bytes} bytes, {kbps} kbps, {bpp} bpp")

    total_bytes = texture_bytes
    motion_y_bytes = os.path.getsize("/tmp/image_IPP_y.mp4")
    kbps = motion_y_bytes*8/sequence_time/1000
    print(f"motion (Y direction): {motion_y_bytes} bytes, {kbps} kbps")

    total_bytes += motion_y_bytes
    motion_x_bytes = os.path.getsize("/tmp/image_IPP_x.mp4")
    kbps = motion_x_bytes*8/sequence_time/1000
    print(f"motion (X direction): {motion_x_bytes} bytes, {kbps} kbps")

    total_bytes += motion_x_bytes
    kbps = total_bytes*8/sequence_time/1000
    bpp = total_bytes*8/(frame_width*frame_height*n_channels*n_frames)
    print(f"total: {kbps} kbps, {bpp} bpp")

    return kbps, bpp
