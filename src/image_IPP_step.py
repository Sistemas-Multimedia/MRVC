''' MRVC/image_IPP_step.py '''

import DWT
import numpy as np
import L_LP as L
import H_LP as H
import deadzone as Q
import motion
import frame
import colors
import cv2
import YCoCg as YUV

VIDEO_PREFIX = "../sequences/complete_stockholm/"
CODESTREAM_PREFIX = "/tmp/"
DECODED_VIDEO_PREFIX = "/tmp/decoder_"
#Q_STEP = 128
N_FRAMES = 16

def norm(x):
    return (frame.normalize(x)*255).astype(np.uint8)

def clip(x):
    return(np.clip(x+128, 0 ,255).astype(np.uint8))

def E_codec(E_k, n_levels, q_step, prefix, k):
    decom = DWT.analyze(E_k, n_levels)
    LL = decom[0]
    decom[0] = Q.quantize(LL, q_step)
    for resolution in decom[1:]:
        LH = resolution[0]
        resolution[0] = Q.quantize(LH, q_step)
        HL = resolution[1]
        resolution[1] = Q.quantize(HL, q_step)
        HH = resolution[2]
        resolution[2] = Q.quantize(HH, q_step)
    DWT.write(q_decom, prefix, k, n_levels)
    LL = q_decom[0]
    dq_decom = Q.dequantize(LL, q_step)
    for resolution in q_decom[1:]:
        LH = resolution[0]
        resolution[0] = Q.dequantize(LH, q_step)
        HL = resolution[1]
        resolution[1] = Q.dequantize(HL, q_step)
        LH = resolution[1]
        resolution[1] = Q.dequantize(HH, q_step)
    dq_E_k = DWT.synthesize(dq_decom)
    return dq_E_k

def V_codec(motion, n_levels, delta, prefix, k):
    decom_Y = pywt.wavedec2(motion[:,:,0], 'db1', mode='per', levels=3)
    decom_X = pywt.wavedec2(motion[:,:,1], 'db1', mode='per', levels=3)
    L.write(decom_Y[0], prefix, k)
    L.write(decom_Y[1], prefix, k)
    H_subbands_decom_Y = decom_Y[1:]
    for resolution in H_subbands_decom_Y:
        resolution[0][:,:] = 0
        resolution[1][:,:] = 0
        resolution[2][:,:] = 0
    H_subbands_decom_X = decom_X[1:]
    for resolution in H_subbands_decom_X:
        resolution[0][:,:] = 0
        resolution[1][:,:] = 0
        resolution[2][:,:] = 0
    pywt.waverec2(decom_Y, 'db1')
    pywt.waverec2(decom_X, 'db1')
    _motion = np.empty_like(motion)
    _motion[:,:,0] = decom_Y[:,:]
    _motion[:,:,0] = decom_X[:,:]
    return _motion

def encode(video=VIDEO_PREFIX, codestream=CODESTREAM_PREFIX, n_frames=N_FRAMES, q_step=Q.step):
    try:
        k = 0
        W_k = frame.read(f"{video}{k:03d}")
        V_k = YUV.from_RGB(W_k) # (a)
        V_k_1 = V_k # (b)
        E_k = V_k # (d)
        dequantized_E_k = E_codec(E_k, 5, q_step, codestream, 0) # (g and h)
        reconstructed_V_k = dequantized_E_k # (i)
        frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_{k:03d}") # Decoder's output
        reconstructed_V_k_1 = reconstructed_V_k # (j)
        for k in range(1, n_frames):
            W_k = frame.read(f"{video}{k:03d}")
            V_k = YUV.from_RGB(V_k) # (a)
            flow = motion.estimate(V_k[:,:,0], V_k_1[:,:,0]) # (c)
            V_k_1 = V_k # (b)
            prediction_V_k = motion.make_prediction(reconstructed_V_k_1, flow) # (i)
            frame.debug_write(clip(prediction_V_k), f"{codestream}encoder_prediction_{k:03d}")
            E_k = V_k - prediction_V_k # (d)
            frame.debug_write(clip(E_k), f"{codestream}encoder_prediction_error_{k:03d}")
            quantized_E_k = Q.quantize(E_k, step=q_step) # (e)
            dequantized_E_k = Q.dequantize(quantized_E_k, step=q_step) # (f)
            frame.debug_write(clip(dequantized_E_k), f"{codestream}encoder_dequantized_prediction_error_{k:03d}")
            reconstructed_V_k = dequantized_E_k + prediction_V_k # (g)
            #L.write(reconstructed_V_k, video + "reconstructed", k)
            frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_{k:03d}") # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (h)
            L.write(flow[:,:,0], codestream, k) # (k)
            L.write(flow[:,:,1], codestream, k) # (k)
            H.write(quantized_E_k, codestream, k) # (j)
    except:
        print(colors.red(f'IPP_step.encode(video="{video}", codestream="{codestream}", n_frames={n_frames}, q_step={q_step})'))
        raise
