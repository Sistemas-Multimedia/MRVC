''' MRVC/hybrid.py '''

import numpy as np
import cv2
import deadzone
import YCoCg
import DWT
import motion

PREFIX = "../sequences/stockholm/"
Q_STEP = 1

def load_frame(prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}{ASCII_frame_number}.png"
    frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.array(frame)
    return frame # [rows, columns, components]

def write_frame(frame, prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    cv2.imwrite(f"{prefix}{ASCII_frame_number}.png", frame)

def read_L(prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}LL{ASCII_frame_number}.png"
    subband = cv2.imread(fn, cv2.IMREAD_UNCHANGED) # [rows, columns, components]
    subband = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    subband = np.array(subband, dtype=np.float64)
    subband -= 32768.0
    return subband # [rows, columns, components]

def write_L(L, prefix, frame_number):
    #print(L.shape)
    subband = np.array(L, dtype=np.float64)
    #subband = subband.astype(np.float64)
    subband += 32768.0
    subband = subband.astype(np.uint16)
    ASCII_frame_number = str(frame_number).zfill(3)
    cv2.imwrite(f"{prefix}LL{ASCII_frame_number}.png", subband)

def read_H(prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    H = []
    sb = 0
    for sbn in subband_names:
        fn = f"{prefix}{sbn}{ASCII_frame_number}.png"
        subband = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
        subband = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        subband = np.array(subband, dtype=np.float64)
        subband -= 32768.0
        H.append(subband)
    return H # [LH, HL, HH], each one [rows, columns, components]

def write_H(H, prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    sb = 0
    for sbn in subband_names:
        subband = np.array(H[sb], dtype=np.float64)
        #subband = H[i].astype(np.float32)
        subband += 32768.0
        subband = subband.astype(np.uint16)
        cv2.imwrite(f"{prefix}{sbn}{ASCII_frame_number}.png", subband)
        sb += 1

def interpolate_L(L):
    #H = ((None, None, None))*3
    #H = [(None, None, None)]*3
    #H = (None, None, None)
    LH = np.zeros(shape=(L.shape), dtype=np.float64)
    HL = np.zeros(shape=(L.shape), dtype=np.float64)
    HH = np.zeros(shape=(L.shape), dtype=np.float64)
    H = (LH, HL, HH)
    _L_ = DWT.synthesize(L, H)
    return _L_

def reduce_L(_L_):
    L, _ = DWT.analyze(_L_)
    return L

def interpolate_H(H):
    #L = [None]*3
    LL = np.zeros(shape=(H[0].shape), dtype=np.float64)
    _H_ = DWT.synthesize(LL, H)
    return _H_

def reduce_H(_H_):
    _, H = DWT.analyze(_H_)
    return H

def encode(prefix=PREFIX, n_frames=5):
    k = 0
    ASCII_k = str(k).zfill(3)
    V_k = load_frame(prefix, ASCII_k)
    V_k = YCoCg.from_RGB(V_k)
    V_k_L, V_k_H = DWT.analyze(V_k) # (a)
    _V_k_L = interpolate_L(V_k_L) # (b)
    _V_k_1_L = _V_k_L # (c)
    _V_k_H = interpolate_H(V_k_H) # (h)
    _E_k_H = _V_k_H # (i)
    quantized__E_k_H = deadzone.quantize(_E_k_H, q_step=Q_STEP) # (j)
    dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=Q_STEP) # (k)
    reconstructed__V_k_H = dequantized__E_k_H # (l)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (m)
    quantized_E_k_H = reduce_H(quantized__E_k_H) # (o)
    write_L(V_k_L, prefix, ASCII_k) # (p)
    write_H(quantized_E_k_H, prefix, ASCII_k) # (p)
    for k in range(1, n_frames):
        ASCII_k = str(k).zfill(3)
        V_k = load_frame(prefix, ASCII_k)
        V_k = YCoCg.from_RGB(V_k)
        V_k_L, V_k_H = DWT.analyze(V_k) # (a)
        _V_k_L = interpolate_L(V_k_L) # (b)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (d)
        prediction__V_k_L = motion.predict(_V_k_1_L, flow) # (e)
        _V_k_1_L = _V_k_L # (c)
        _E_k_L = _V_k_L - prediction__V_k_L # (f)
        S_k = _E_k_L < _V_k_L # (g)
        _V_k_H = interpolate_H(V_k_H) # (h)
        prediction__V_k_H = motion.predict(reconstructed__V_k_1_H, flow) # (n)
        IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, _V_k_H) # (?)
        _E_k_H = _V_k_H - IP_prediction__V_k_H # (i)
        quantized__E_k_H = deadzone.quantize(_E_k_H, q_step=Q_STEP) # (j)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=Q_STEP) # (k)
        reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (l)
        write_H(reconstructed__V_k_H, "/tmp/reconstructed_encoder_", ASCII_k)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (m)

        quantized_E_k_H = reduce_H(quantized__E_k_H) # (o)
        write_L(V_k_L, prefix, ASCII_k) # (p)
        write_H(quantized_E_k_H, prefix, ASCII_k) # (p)
    
def decode(prefix=PREFIX, n_frames=5):
    k = 0
    V_k_L = read_L(prefix, ASCII_k) # (q)
    quantized_E_k_H = read_H(prefix, ASCII_k) # (q)
    quantized__E_k_H = interpolate_H(quantized_E_k_H) # (r)
    _V_k_L = interpolate_L(V_k_L) # (b)
    _V_k_1_L = _V_k_L # (c)
    dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H) # (k)
    reconstructed__V_k_H = dequantized__E_k_H # (l)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (m)
    reconstructed_V_k_H = reduce_H(reconstructed__V_k_H) # (s)
    reconstructed_V_k = DWT.synthesize(V_k_L, reconstructed_V_k_H) # (t)
    reconstructed_V_k = YCoCg.to_RGB(reconstructed_V_k)
    write_frame(reconstructed_V_k, prefix, ASCII_k)
    for k in range(1, n_frames):
        ASCII_k = str(k).zfill(3)
        V_k_L = read_L(prefix, ASCII_k) # (q)
        quantized_E_k_H = read_H(prefix, ASCII_k) # (q)
        _V_k_L = interpolate_L(V_k_L) # (b)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (d)
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
        reconstructed_V_k = YCoCg.to_RGB(reconstructed_V_k)
        write_frame(reconstructed_V_k, prefix + "reconstructed_decoder", ASCII_k)

encode()
