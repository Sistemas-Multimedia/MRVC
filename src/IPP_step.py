''' MRVC/IPP_step.py '''

import numpy as np
import DWT
import deadzone
import motion
import frame
import L
import H

VIDEO_PREFIX = "../sequences/complete_stockholm/"
CODESTREAM_PREFIX = "/tmp/"
DECODED_VIDEO_PREFIX = "/tmp/decoder_"
Q_STEP = 128
N_FRAMES = 16

class Encoder():

    def __init__(self, video=VIDEO_PREFIX, codestream=CODESTREAM_PREFIX, q_step=Q_STEP):
        self.video = video
        self.codestream = codestream
        self.q_step = q_step
        self.k = 0

        # Encode first frame
        self.V_k = frame.read(self.video, self.k)
        self.V_k_L, self.V_k_H = DWT.analyze_step(V_k) # (a)
        L.write(V_k_L, self.codestream, self.k) # (g)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        self._V_k_1_L = _V_k_L # (E.b)
        _V_k_H = H.interpolate(V_k_H) # (b)
        _E_k_H = _V_k_H # (c)
        quantized__E_k_H = deadzone.quantize(_E_k_H, self.q_step) # (d)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, self.q_step) # (E.g)
        reconstructed__V_k_H = dequantized__E_k_H # (E.h)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
        H.write(quantized_E_k_H, self.codestream, self.k) # (g)

    def encode_next_frame(self):
        V_k = frame.read(self.video, self.k)
        V_k_L, V_k_H = DWT.analyze_step(V_k) # (a)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (E.c)
        prediction__V_k_L = motion.predict(_V_k_1_L, flow) # (E.d)
        frame.debug_write(prediction__V_k_L, codestream + "encoder_prediction_L_", self.k)
        _V_k_1_L = _V_k_L # (E.b)
        _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
        frame.debug_write(_V_k_L, self.codestream + "encoder_predicted_L_", self.k)
        S_k = _E_k_L < _V_k_L # (E.f)
        if __debug__:
            unique, counts = np.unique(S_k, return_counts=True)
            print(unique, counts)
        frame.debug_write(S_k, self.codestream + "encoder_selection_", self.k)
        _V_k_H = H.interpolate(V_k_H) # (b)
        frame.debug_write(_V_k_H + 128, codestream + "encoder_predicted_H_", self.k)
        prediction__V_k_H = motion.predict(reconstructed__V_k_1_H, flow) # (E.j)
        frame.debug_write(prediction__V_k_H + 128, codestream + "encoder_prediction_H_", self.k)
        IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
        frame.write(IP_prediction__V_k_H + 128, self.codestream + "encoder_IP_prediction_H_", self.k)
        _E_k_H = _V_k_H - IP_prediction__V_k_H # (c)
        frame.debug_write(_E_k_H + 128, codestream + "encoder_prediction_error_H_", self.k)
        quantized__E_k_H = deadzone.quantize(_E_k_H, self.q_step) # (d)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, self.q_step) # (E.g)
        reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (E.h)
        frame.debug_write(reconstructed__V_k_H + 128, self.codestream + "encoder_reconstructed_", self.k)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
        L.write(V_k_L, self.codestream, self.k) # (g)
        H.write(quantized_E_k_H, self.codestream, self.k) # (g)

def encode(video=VIDEO_PREFIX, codestream=CODESTREAM_PREFIX, n_frames=N_FRAMES, q_step=Q_STEP):
    k = 0
    V_k = frame.read(video, k)
    #V_k = YCoCg.from_RGB(V_k)
    V_k_L, V_k_H = DWT.analyze_step(V_k) # (a)
    #L.write(YCoCg.to_RGB(V_k_L), codestream, k) # (g)
    L.write(V_k_L, codestream, k) # (g)
    _V_k_L = L.interpolate(V_k_L) # (E.a)
    _V_k_1_L = _V_k_L # (E.b)
    _V_k_H = H.interpolate(V_k_H) # (b)
    _E_k_H = _V_k_H # (c)
    quantized__E_k_H = deadzone.quantize(_E_k_H, q_step=q_step) # (d)
    dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=q_step) # (E.g)
    reconstructed__V_k_H = dequantized__E_k_H # (E.h)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
    quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
    H.write(quantized_E_k_H, codestream, k) # (g)
    for k in range(1, n_frames):
        V_k = frame.read(video, k)
        #V_k = YCoCg.from_RGB(V_k)
        V_k_L, V_k_H = DWT.analyze_step(V_k) # (a)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (E.c)
        prediction__V_k_L = motion.predict(_V_k_1_L, flow) # (E.d)
        frame.debug_write(prediction__V_k_L, codestream + "encoder_prediction_L_", k)
        _V_k_1_L = _V_k_L # (E.b)
        _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
        frame.debug_write(_V_k_L, codestream + "encoder_predicted_L_", k)
        S_k = _E_k_L < _V_k_L # (E.f)
        if __debug__:
            unique, counts = np.unique(S_k, return_counts=True)
            print(unique, counts)
        frame.debug_write(S_k, codestream + "encoder_selection_", k)
        _V_k_H = H.interpolate(V_k_H) # (b)
        frame.debug_write(_V_k_H + 128, codestream + "encoder_predicted_H_", k)
        prediction__V_k_H = motion.predict(reconstructed__V_k_1_H, flow) # (E.j)
        frame.debug_write(prediction__V_k_H + 128, codestream + "encoder_prediction_H_", k)
        IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
        #IP_prediction__V_k_H = np.zeros_like(S_k) # (E.k)
        frame.write(IP_prediction__V_k_H + 128, codestream + "encoder_IP_prediction_H_", k)
        _E_k_H = _V_k_H - IP_prediction__V_k_H # (c)
        #assert (IP_prediction__V_k_H == 0).all()
        #assert (_E_k_H == _V_k_H).all()
        print("IP_prediction__V_k_H.max() =", IP_prediction__V_k_H.max())
        frame.debug_write(_E_k_H + 128, codestream + "encoder_prediction_error_H_", k)
        quantized__E_k_H = deadzone.quantize(_E_k_H, q_step=q_step) # (d)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=q_step) # (E.g)
        #for i in range(dequantized__E_k_H.shape[0]):
        #    for j in range(dequantized__E_k_H.shape[1]):
        #        for k in range(dequantized__E_k_H.shape[2]):
        #            if dequantized__E_k_H[i,j,k] != _E_k_H[i,j,k]:
        #                print(dequantized__E_k_H[i,j,k], _E_k_H[i,j,k])

        #assert (dequantized__E_k_H == _E_k_H.astype(np.int16)).all()
        reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (E.h)
        #assert (reconstructed__V_k_H == _V_k_H.astype(np.int16)).all()
        frame.debug_write(reconstructed__V_k_H + 128, codestream + "encoder_reconstructed_", k)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
        #L.write(YCoCg.to_RGB(V_k_L), codestream, k) # (g)
        L.write(V_k_L, codestream, k) # (g)
        H.write(quantized_E_k_H, codestream, k) # (g)


class Decoder():

    def __init__(self, codestream=CODESTREAM_PREFIX, video=DECODED_VIDEO_PREFIX, q_step=Q_STEP):
        self.video = video
        self.codestream = codestream
        self.q_step = q_step
        self.k = 0

        # Decode first frame
        self.k = 0
        V_k_L = L.read(self.codestream, self.k) # (h)
        quantized_E_k_H = H.read(self.codestream, self.k) # (h)
        quantized__E_k_H = H.interpolate(quantized_E_k_H) # (i)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        _V_k_1_L = _V_k_L # (E.b)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step) # (E.g)
        reconstructed__V_k_H = dequantized__E_k_H # (E.h)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        reconstructed_V_k_H = H.reduce(reconstructed__V_k_H) # (i)
        reconstructed_V_k = DWT.synthesize_step(V_k_L, reconstructed_V_k_H) # (k)
        reconstructed_V_k = np.clip(reconstructed_V_k, 0, 255)
        frame.write(reconstructed_V_k, self.video, self.k)
        

    def decode_next_frame(self):
        V_k_L = L.read(self.codestream, self.k) # (h)
        quantized_E_k_H = H.read(self.codestream, self.k) # (h)
        quantized__E_k_H = H.interpolate(quantized_E_k_H) # (i)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (E.c)
        prediction__V_k_L = motion.predict(_V_k_1_L, flow) # (E.d)
        _V_k_1_L = _V_k_L # (E.b)
        _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
        S_k = _E_k_L < _V_k_L # (E.f)
        prediction__V_k_H = motion.predict(reconstructed__V_k_1_H, flow) # (E.j)
        IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
        dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, self.q_step) # (E.g)
        reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H # (E.h)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        reconstructed_V_k_H = H.reduce(reconstructed__V_k_H) # (j)
        reconstructed_V_k = DWT.synthesize_step(V_k_L, reconstructed_V_k_H) # (k)
        reconstructed_V_k = np.clip(reconstructed_V_k, 0, 255)
        frame.write(reconstructed_V_k, self.video, self.k)

def decode(codestream=CODESTREAM_PREFIX, video=DECODED_VIDEO_PREFIX, n_frames=N_FRAMES, q_step=Q_STEP):
    k = 0
    #V_k_L = YCoCg.from_RGB(L.read(codestream, k)) # (h)
    V_k_L = L.read(codestream, k) # (h)
    quantized_E_k_H = H.read(codestream, k) # (h)
    quantized__E_k_H = H.interpolate(quantized_E_k_H) # (i)
    _V_k_L = L.interpolate(V_k_L) # (E.a)
    #assert (quantized__E_k_H.shape == _V_k_L.shape).all()
    _V_k_1_L = _V_k_L # (E.b)
    dequantized__E_k_H = deadzone.dequantize(quantized__E_k_H, q_step=q_step) # (E.g)
    reconstructed__V_k_H = dequantized__E_k_H # (E.h)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
    reconstructed_V_k_H = H.reduce(reconstructed__V_k_H) # (i)
    reconstructed_V_k = DWT.synthesize_step(V_k_L, reconstructed_V_k_H) # (k)
    #reconstructed_V_k = YCoCg.to_RGB(reconstructed_V_k)
    reconstructed_V_k = np.clip(reconstructed_V_k, 0, 255)
    frame.write(reconstructed_V_k, video, k)
    for k in range(1, n_frames):
        #V_k_L = YCoCg.from_RGB(L.read(codestream, k)) # (h)
        V_k_L = L.read(codestream, k) # (h)
        quantized_E_k_H = H.read(codestream, k) # (h)
        quantized__E_k_H = H.interpolate(quantized_E_k_H) # (i)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0]) # (E.c)
        prediction__V_k_L = motion.predict(_V_k_1_L, flow) # (E.d)
        _V_k_1_L = _V_k_L # (E.b)
        _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
        S_k = _E_k_L < _V_k_L # (E.f)
        prediction__V_k_H = motion.predict(reconstructed__V_k_1_H, flow) # (E.j)
        IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
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
        reconstructed_V_k = DWT.synthesize_step(V_k_L, reconstructed_V_k_H) # (k)
        #reconstructed_V_k = YCoCg.to_RGB(reconstructed_V_k)
        reconstructed_V_k = np.clip(reconstructed_V_k, 0, 255)
        frame.write(reconstructed_V_k, video, k)
