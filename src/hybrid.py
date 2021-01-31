''' MRVC/hybrid.py '''

import numpy as np
import deadzone
import YCoCg
import DWT
import cv2
import motion

PREFIX = "../sequences/stockholm/"

def load_frame(prefix=PREFIX):
    fn = f"{prefix}.png"
    frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED) # [rows, columns, components]
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.array(frame)
    return frame

def write_frame(frame, prefix=PREFIX):
    cv2.imwrite(f"{prefix}.png", frame)
    
def write_L(subband, prefix=PREFIX):
    subband = frame.astype(np.float32)
    subband += 32768.0
    subband = frame.astype(np.uint16)
    cv2.imwrite(f"{prefix}LL.png", subband)

def read_L(prefix=PREFIX):
    fn = f"{prefix}.png"
    frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED) # [rows, columns, components]
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.array(frame)
    return frame

def write_H(subbands, prefix=PREFIX):
    subbands = ["LH", "HL", "HH"]
    c = 0
    for i in subbands:
        subband = i.astype(np.float32)
        subband += 32768.0
        subband = frame.astype(np.uint16)
        cv2.imwrite(f"{prefix}{subbands[c]}.png", subband)
        c += 1

def interpolate_L(L):
    _L_ = DWT.synthesize([L, [None, None, None]])
    return _L_

def reduce_L(_L_):
    L, _ = DWT.analyze(_L_)
    return L

def interpolate_H(H):
    _H_ = DWT.synthesize(None, H)
    return _H_

def reduce_H(_H_):
    _, H = DWT.analyze(_H_)
    return H

def encode(prefix=PREFIX, n_frames=5):
    k = 0
    ASCII_k = str(k).zfill(3)
    V_k = load_frame(prefix + ASCII_k)
    V_k_L, V_k_H = DWT.analyze(V_k) # (a)
    _V_k_L = interpolate_L(V_k_L) # (b)
    _V_k_1_L = _V_k_L # (c)
    _E_k_H = _V_k_H # (i)
    quantized__E_k_H = deadzone.quantize(_E_k_H) # (j)
    dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H) # (k)
    reconstructed__V_k_H = dequantized__E_k_H # (l)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (m)
    quantized_E_k_H = reduce_H(quantized__E_k_H) # (o)
    write_L(V_k_L, prefix + ASCII_k) # (p)
    write_H(quantized_E_k_H, prefix + ASCII_k) # (p)
    for k in range(1, number_of_frames):
        ASCII_k = str(k).zfill(3)
        V_k = load_frame(prefix + ASCII_k)
        V_k_L, V_k_H = DWT.analyze(V_k) # (a)
        _V_k_L = interpolate_L(V_k_L) # (b)
        flow = motion.estimate(_V_k_L, _V_k_1_L) # (d)
        prediction__V_k_L = motion.predict(_V_k_1_L, flow) # (e)
        _V_k_1_L = _V_k_l # (c)
        _E_k_L = _V_k_L - prediction__V_k_L # (f)
        S_k = _E_k_L < _V_k_L # (g)
        _V_k_H = interpolate_H(V_k_H) # (h)
        prediction__V_k_H = motion.predict(reconstructed_V_k_1_H, flow) # (n)
        IP_prediction__V_k_H = np.where(S_k, prediction_V_k_H, _V_k_H) # (?)
        _E_k_H = _V_k_H - IP_prediction_V_k_H # (i)
        quantized__E_k_H = deadzone.quantize(E_k_H) # (j)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H) # (k)
        reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (l)
        write_H(reconstructed__V_k_H, prefix + "reconstructed_encoder" + ASCII_k)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (m)

        quantized_E_k_H = reduce_H(quantized__E_k_H) # (o)
        write_L(V_k_L, prefix + ASCII_k) # (p)
        write_H(quantized_E_k_H, prefix + ASCII_k) # (p)
    
def decode(prefix=PREFIX, n_frames=5):
    k = 0
    ASCII_k = str(k).zfill(3)
    V_k_L = read_L(prefix + ASCII_k) # (q)
    quantized_E_k_H = read_H(prefix + ASCII_k) # (q)
    quantized__E_k_H = interpolate_H(quantized_E_k_H) # (r)
    _V_k_L = interpolate_L(V_k_L) # (b)
    _V_k_1_L = _V_k_L # (c)
    dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H) # (k)
    reconstructed__V_k_H = dequantized__E_k_H # (l)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (m)
    reconstructed_V_k_H = reduce_H(reconstructed__V_k_H) # (s)
    reconstructed_V_k = DWT.synthesize(V_k_L, reconstructed_V_k_H) # (t)
    write_frame(reconstructed_V_k, prefix + ASCII_k)
    for k in range(1, number_of_frames):
        ASCII_k = str(k).zfill(3)
        V_k_L = read_L(prefix + ASCII_k) # (q)
        quantized_E_k_H = read_H(prefix +  ASCII_k) # (q)
        _V_k_L = interpolate_L(V_k_L) # (b)
        flow = motion.estimate(_V_k_L, _V_k_1_L) # (d)
        prediction__V_k_L = motion.predict(_V_k_1_L, flow) # (e)
        _V_k_1_L = _V_k_l # (c)
        _E_k_L = _V_k_L - prediction__V_k_L # (f)
        S_k = _E_k_L < _V_k_L # (g)
        prediction__V_k_H = motion.predict(reconstructed_V_k_1_H, flow) # (n)
        IP_prediction__V_k_H = np.where(S_k, prediction_V_k_H, _V_k_H) # (?)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H) # (k)
        reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (l)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (m)
        reconstructed_V_k_H = reduce_H(reconstructed_V_k_H) # (s)
        reconstructed_V_k = DWT.synthesize(V_k_L, reconstructed_V_k_H) # (t)
        write_frame(reconstructed_V_k, prefix + "reconstructed_decoder" + ASCII_k)

encode()
