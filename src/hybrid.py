''' MRVC/hybrid.py '''

import numpy as np
import deadzone
import YCoCg
import DWT
import cv2
import motion

x_size = 1280
y_size = 768
prefix = "."

def load_frame(prefix):
    fn = f"{prefix}.png"
    frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED) # [rows, columns, components]
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.array(frame)
    return frame

def write_frame(frame, prefix):
    cv2.imwrite(f"{prefix}.png", frame)

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
    _, H = DWT.analyze(_H_])
    return H

def encode(path_to_the_sequence, number_of_frames):
    reconstructed_V_k_1 = np.zeros((y_size, x_size, 3))
    _V_k_1_L = np.zeros((y_size, x_size, 3))
    prediction_V_k_H = np.zeros((y_size, x_size, 3))
    for k in range(number_of_frames):
        ASCII_k = str(k).zfill(3)
        V_k = load_frame(prefix + ASCII_k + ".png")
        V_k_L, V_k_H = DWT.analyze(V_k)
        _V_k_L = interpolate_L(V_k_L)
        flow = motion.estimate(_V_k_L, _V_k_1_L)
        prediction_V_k_L = motion.predict(_V_k_1_L, flow)
        _E_k_L = _V_k_L - prediction_V_k_L
        M_k = _E_k_L < _V_k_L
        _V_k_H = interpolate_H(V_k_H)
        _E_k_H = _V_k_H - prediction_V_k_H
        quantized_E_k_H = deadzone.quantize(E_k_H)
        write_frame(quantized_E_k_H, prefix + ASCII_k + "_H")
        write_frame(V_k_L, prefix + ASCII_k + "_L")
        dequantized_E_k_H = deadzone.dequentize(quantized_E_k_H)
        reconstructed_V_k_H = dequantized_E_k_H + prediction_V_k_H
        reconstructed_V_k_1_H = reconstructed_V_k_H
        prediction_V_k_H = motion.predict(_V_k_1_H, flow)
        prediction_V_k_H = np.where(M_k, prediction_V_k_H, _V_k_H)
        
reconstructed_F_k_1 = 0
for k in range(10):
    F_k = k + 10 # The signal to encode
    prediction_F_k = P(reconstructed_F_k_1)
    E_k = F_k - prediction_F_k
    quantized_E_k = Q(E_k)
    dequantized_E_k = iQ(quantized_E_k)
    reconstructed_F_k = dequantized_E_k + prediction_F_k
    reconstructed_F_k_1 = reconstructed_F_k  # The Z^-1 delay is simulated 
                                             # using in the next iteration of the loop
                                             # The current value for reconstructed_F_k
    codestream.append(E(quantized_E_k))

