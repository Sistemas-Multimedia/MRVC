''' MRVC/IPP_step.py '''

import numpy as np
#import DWT as spatial_transform
import LP as spatial_transform
#import L_DWT as L
import L_LP as L
#import H_DWT as H
import H_LP as H
import deadzone
import motion
import frame
import colors
import cv2

VIDEO_PREFIX = "../sequences/complete_stockholm/"
CODESTREAM_PREFIX = "/tmp/"
DECODED_VIDEO_PREFIX = "/tmp/decoder_"
Q_STEP = 128
N_FRAMES = 16

def norm(x):
    return (frame.normalize(x)*255).astype(np.uint8)

def clip(x):
    return(np.clip(x+128, 0 ,255).astype(np.uint8))

#def encode(L_sequence=CODESTREAM_PREFIX + "L", H_sequence=CODESTREAM_PREFIX + "H", codestream=CODESTREAM_PREFIX, n_frames=N_FRAMES, q_step=Q_STEP):
def encode(video=VIDEO_PREFIX, codestream=CODESTREAM_PREFIX, n_frames=N_FRAMES, q_step=Q_STEP):
    try:
        k = 0
        #V_k = frame.read(video, k)
        #V_k = YCoCg.from_RGB(V_k)
        #V_k_L, V_k_H = DWT.analyze_step(V_k) # (a)
        V_k_L = L.read(video, k)#V_k_L = L.read(L_sequence, k)
        V_k_H = H.read(video, k, V_k_L.shape)#V_k_H = H.read(H_sequence, k)
        #L.write(YCoCg.to_RGB(V_k_L), codestream, k) # (g)
        L.write(V_k_L, codestream, k) # (g)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        _V_k_1_L = _V_k_L # (E.b)
        _V_k_H = H.interpolate(V_k_H) # (b)
        _E_k_H = _V_k_H # (c)
        quantized__E_k_H = deadzone.quantize(_E_k_H, q_step=q_step) # (d)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=q_step) # (E.g)
        reconstructed__V_k_H = dequantized__E_k_H # (E.h)
        #frame.write(reconstructed__V_k_H, video + "reconstructed_H", k)
        L.write(reconstructed__V_k_H, video + "reconstructed_H", k)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
        H.write(quantized_E_k_H, codestream, k) # (g)
        for k in range(1, n_frames):
            #V_k = frame.read(video, k)
            #V_k = YCoCg.from_RGB(V_k)
            #V_k_L, V_k_H = DWT.analyze_step(V_k) # (a)
            V_k_L = L.read(video, k)#V_k_L = L.read(L_sequence, k)
            V_k_H = H.read(video, k, V_k_L.shape)#V_k_H = H.read(H_sequence, k)
            _V_k_L = L.interpolate(V_k_L) # (E.a)
            flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (E.c)
            print("------------->", _V_k_L[:,:,0].dtype, _V_k_1_L[:,:,0].dtype)
            prediction__V_k_L = motion.make_prediction(_V_k_1_L, flow) # (E.d)
            frame.debug_write(norm(prediction__V_k_L), f"{codestream}encoder_prediction_L_{k:03d}")
            _V_k_1_L = _V_k_L # (E.b)
            _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
            frame.debug_write(norm(_V_k_L), f"{codestream}encoder_predicted_L_{k:03d}")
            frame.debug_write(clip(_E_k_L), f"{codestream}encoder_prediction_error_L_{k:03d}")
            S_k = _E_k_L[:,:,0] < _V_k_L[:,:,0] # (E.f)
            if __debug__:
                unique, counts = np.unique(S_k, return_counts=True)
                #print(unique, counts)
                print("Number of I-type coeffs =", counts[0])
                if len(unique) > 1:
                    print("Number of P-type coeffs =", counts[1])
            frame.debug_write(cv2.merge((S_k.astype(np.uint8),S_k.astype(np.uint8),S_k.astype(np.uint8))), f"{codestream}encoder_selection_{k:03d}")
            _V_k_H = H.interpolate(V_k_H) # (b)
            frame.debug_write(clip(_V_k_H), f"{codestream}encoder_predicted_H_{k:03d}")
            prediction__V_k_H = motion.make_prediction(reconstructed__V_k_1_H, flow) # (E.j)
            frame.debug_write(clip(prediction__V_k_H), f"{codestream}encoder_prediction_H_{k:03d}")
            #IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
            IP_prediction__V_k_H = np.empty_like(prediction__V_k_H)
            for c in range(3):
                #IP_prediction__V_k_H[:,:,c] = np.zeros_like(S_k) # (E.k)
                IP_prediction__V_k_H[:,:,c] = np.where(S_k, prediction__V_k_H[:,:,c], 0) # (E.k)
                #IP_prediction__V_k_H[:,:,c] = np.where(S_k, 0, prediction__V_k_H[:,:,c]) # (E.k)
            #IP_prediction__V_k_H[:,:,0] = np.where(S_k, prediction__V_k_H[:,:,0], 0) # (E.k)
            #IP_prediction__V_k_H[:,:,1] = np.where(S_k, prediction__V_k_H[:,:,1], 0) # (E.k)
            #IP_prediction__V_k_H[:,:,2] = np.where(S_k, prediction__V_k_H[:,:,2], 0) # (E.k)
            #IP_prediction__V_k_H = np.zeros_like(S_k) # (E.k)
            #IP_prediction__V_k_H = prediction__V_k_H
            frame.debug_write(clip(IP_prediction__V_k_H), f"{codestream}encoder_IP_prediction_H_{k:03d}")
            _E_k_H = _V_k_H - IP_prediction__V_k_H # (c)
            #assert (IP_prediction__V_k_H == 0).all()
            #assert (_E_k_H == _V_k_H).all()
            #print("IP_prediction__V_k_H.max() =", IP_prediction__V_k_H.max())
            frame.debug_write(clip(_E_k_H), f"{codestream}encoder_prediction_error_H_{k:03d}")
            quantized__E_k_H = deadzone.quantize(_E_k_H, q_step=q_step) # (d)
            dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=q_step) # (E.g)
            #for i in range(dequantized__E_k_H.shape[0]):
            #    for j in range(dequantized__E_k_H.shape[1]):
            #        for k in range(dequantized__E_k_H.shape[2]):
            #            if dequantized__E_k_H[i,j,k] != _E_k_H[i,j,k]:
            #                print(dequantized__E_k_H[i,j,k], _E_k_H[i,j,k])
            frame.debug_write(clip(dequantized__E_k_H), f"{codestream}encoder_dequantized_prediction_error_H_{k:03d}")
            #assert (dequantized__E_k_H == _E_k_H.astype(np.int16)).all()
            reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (E.h)
            #frame.write(reconstructed__V_k_H, video + "reconstructed_H", k) # Ojo, reconstructed__V_k_H está a 16 bits!!
            L.write(reconstructed__V_k_H, video + "reconstructed_H", k)
            #print("->", reconstructed__V_k_H.max(), reconstructed__V_k_H.min())
            #assert (reconstructed__V_k_H == _V_k_H.astype(np.int16)).all()
            frame.debug_write(clip(reconstructed__V_k_H), f"{codestream}encoder_reconstructed_{k:03d}")
            reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
            quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
            #L.write(YCoCg.to_RGB(V_k_L), codestream, k) # (g)
            L.write(V_k_L, codestream, k) # (g)
            H.write(quantized_E_k_H, codestream, k) # (g)
    except:
        print(colors.red(f'IPP_step.encode(video="{video}", codestream="{codestream}", n_frames={n_frames}, q_step={q_step})'))
        raise

def decode(codestream=CODESTREAM_PREFIX, video=DECODED_VIDEO_PREFIX, n_frames=N_FRAMES, q_step=Q_STEP):
        
#def decode(codestream=CODESTREAM_PREFIX, video=DECODED_VIDEO_PREFIX, n_frames=N_FRAMES, q_step=Q_STEP):
    k = 0
    #V_k_L = YCoCg.from_RGB(L.read(codestream, k)) # (h)
    V_k_L = L.read(codestream, k) # (h)
    quantized_E_k_H = H.read(codestream, k, V_k_L.shape) # (h)
    quantized__E_k_H = H.interpolate(quantized_E_k_H) # (i)
    _V_k_L = L.interpolate(V_k_L) # (E.a)
    #assert (quantized__E_k_H.shape == _V_k_L.shape).all()
    _V_k_1_L = _V_k_L # (E.b)
    dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=q_step) # (E.g)
    reconstructed__V_k_H = dequantized__E_k_H # (E.h)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
    reconstructed_V_k_H = H.reduce(reconstructed__V_k_H) # (i)
    reconstructed_V_k = spatial_transform.synthesize_step(V_k_L, reconstructed_V_k_H) # (k)
    #reconstructed_V_k = YCoCg.to_RGB(reconstructed_V_k)
    reconstructed_V_k = np.clip(reconstructed_V_k, 0, 255).astype(np.uint8)
    frame.write(reconstructed_V_k, f"{video}{k:03d}")
    for k in range(1, n_frames):
        #V_k_L = YCoCg.from_RGB(L.read(codestream, k)) # (h)
        V_k_L = L.read(codestream, k) # (h)
        quantized_E_k_H = H.read(codestream, k, V_k_L.shape) # (h)
        quantized__E_k_H = H.interpolate(quantized_E_k_H) # (i)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (E.c)
        prediction__V_k_L = motion.make_prediction(_V_k_1_L, flow) # (E.d)
        _V_k_1_L = _V_k_L # (E.b)
        _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
        S_k = _E_k_L[:,:,0] < _V_k_L[:,:,0] # (E.f)
        prediction__V_k_H = motion.make_prediction(reconstructed__V_k_1_H, flow) # (E.j)
        #IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
        IP_prediction__V_k_H = np.empty_like(prediction__V_k_H)
        IP_prediction__V_k_H[:,:,0] = np.where(S_k, prediction__V_k_H[:,:,0], 0) # (E.k)
        IP_prediction__V_k_H[:,:,1] = np.where(S_k, prediction__V_k_H[:,:,1], 0) # (E.k)
        IP_prediction__V_k_H[:,:,2] = np.where(S_k, prediction__V_k_H[:,:,2], 0) # (E.k)
        #IP_prediction__V_k_H = np.zeros_like(S_k, dtype=np.float64) # (E.k)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=q_step) # (E.g)
        #assert (dequantized__E_k_H.shape == _V_k_L.shape).all()
        reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (E.h)
        #reconstructed__V_k_H = quantized__E_k_H + IP_prediction__V_k_H # (E.h)
        #reconstructed__V_k_H[:,:,:] = 0.0
        #assert (IP_prediction__V_k_H == 0).all()
        #assert (reconstructed__V_k_H == dequantized__E_k_H).all()
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        reconstructed_V_k_H = H.reduce(reconstructed__V_k_H) # (j)
        reconstructed_V_k = spatial_transform.synthesize_step(V_k_L, reconstructed_V_k_H) # (k)
        #reconstructed_V_k = YCoCg.to_RGB(reconstructed_V_k)
        reconstructed_V_k = np.clip(reconstructed_V_k, 0, 255).astype(np.uint8)
        frame.write(reconstructed_V_k, f"{video}{k:03d}")

