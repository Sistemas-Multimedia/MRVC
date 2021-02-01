''' MRVC/hybrid.py '''

import numpy as np
import DWT
import deadzone
import YCoCg
import motion
import frame
import L
import H

INPUT_SEQ = "../sequences/stockholm/"
OUTPUT_SEQ = "/tmp/"
Q_STEP = 16

def encode(input_seq=INPUT_SEQ, output_seq=OUTPUT_SEQ, n_frames=5):
    k = 0
    V_k = frame.read(input_seq, k)
    V_k = YCoCg.from_RGB(V_k)
    V_k_L, V_k_H = DWT.analyze(V_k) # (a)
    _V_k_L = L.interpolate(V_k_L) # (E.a)
    _V_k_1_L = _V_k_L # (E.b)
    _V_k_H = H.interpolate(V_k_H) # (b)
    _E_k_H = _V_k_H # (c)
    quantized__E_k_H = deadzone.quantize(_E_k_H, q_step=Q_STEP) # (d)
    dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=Q_STEP) # (E.g)
    reconstructed__V_k_H = dequantized__E_k_H # (E.h)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
    quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
    L.write(V_k_L, output_seq, k) # (g)
    H.write(quantized_E_k_H, output_seq, k) # (g)
    for k in range(1, n_frames):
        V_k = frame.read(input_seq, k)
        V_k = YCoCg.from_RGB(V_k)
        V_k_L, V_k_H = DWT.analyze(V_k) # (a)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (E.c)
        prediction__V_k_L = motion.predict(_V_k_1_L, flow) # (E.d)
        frame.debug_write(prediction__V_k_L, output_seq + "prediction_L_", k)
        _V_k_1_L = _V_k_L # (E.b)
        _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
        frame.debug_write(_V_k_L, output_seq + "predicted_L_", k)
        S_k = _E_k_L < _V_k_L # (E.f)
        frame.debug_write(S_k*64 + 128, output_seq + "selection_", k)
        _V_k_H = H.interpolate(V_k_H) # (b)
        prediction__V_k_H = motion.predict(reconstructed__V_k_1_H, flow) # (E.j)
        frame.debug_write(prediction__V_k_H + 128, output_seq + "prediction_H_", k)
        IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
        frame.write(IP_prediction__V_k_H + 128, output_seq + "IP_prediction_H_", k)
        _E_k_H = _V_k_H - IP_prediction__V_k_H # (c)
        frame.debug_write(_E_k_H + 128, output_seq + "prediction_error_H_", k)
        quantized__E_k_H = deadzone.quantize(_E_k_H, q_step=Q_STEP) # (d)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=Q_STEP) # (E.g)
        reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (E.h)
        frame.debug_write(reconstructed__V_k_H + 128, output_seq + "reconstructed_encoder_", k)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
        L.write(V_k_L, "/tmp/", k) # (g)
        H.write(quantized_E_k_H, "/tmp/", k) # (g)
    
def decode(input_seq=INPUT_SEQ, output_seq=OUTPUT_SEQ, n_frames=5):
    k = 0
    V_k_L = L.read(input_seq, k) # (h)
    quantized_E_k_H = H.read(input_seq, k) # (h)
    quantized__E_k_H = H.interpolate(quantized_E_k_H) # (i)
    _V_k_L = L.interpolate(V_k_L) # (E.a)
    _V_k_1_L = _V_k_L # (E.b)
    dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H) # (E.g)
    reconstructed__V_k_H = dequantized__E_k_H # (E.h)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
    reconstructed_V_k_H = H.reduce(reconstructed__V_k_H) # (i)
    reconstructed_V_k = DWT.synthesize(V_k_L, reconstructed_V_k_H) # (k)
    reconstructed_V_k = YCoCg.to_RGB(reconstructed_V_k)
    frame.write(reconstructed_V_k, output_seq, k)
    for k in range(1, n_frames):
        V_k_L = L.read(input_seq, k) # (g)
        quantized_E_k_H = H.read(input_seq, k) # (g)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (E.c)
        prediction__V_k_L = motion.predict(_V_k_1_L, flow) # (E.d)
        _V_k_1_L = _V_k_L # (E.b)
        _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
        S_k = _E_k_L < _V_k_L # (E.f)
        prediction__V_k_H = motion.predict(reconstructed__V_k_1_H, flow) # (E.j)
        IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H) # (E.g)
        reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (E.h)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        reconstructed_V_k_H = H.reduce(reconstructed_V_k_H) # (j)
        reconstructed_V_k = DWT.synthesize(V_k_L, reconstructed_V_k_H) # (k)
        reconstructed_V_k = YCoCg.to_RGB(reconstructed_V_k)
        frame.write(reconstructed_V_k, output_seq + "reconstructed_decoder", k)

print("Encoding ...")
encode()

print("Decoding ...")
decode()
