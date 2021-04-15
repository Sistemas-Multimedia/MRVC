''' MRVC/coef_IPP_step.py '''

import config
import numpy as np

if config.transform == "DWT":
    import DWT as spatial_transform
    import L_DWT as L
    import H_DWT as H

if config.transform == "LP":
    import LP as spatial_transform
    import L_LP as L
    import H_LP as H

if config.quantizer == "deadzone":
    import deadzone as Q

    def E_codec(E_k, video, k, q_step):
        q_E_k = Q.quantize(E_k, q_step) # (d)
        H.write(q_E_k, video, k)
        dq_E_k = Q.dequantize(q_E_k, q_step) # (E.g)
        return dq_E_k

if config.quantizer == "H264":

    if config.color == "YCoCg":
        import YCoCg as YUV

    if config.color == "YCrCb":
        import YCrCb as YUV

    if config.color == "RGB":
        import RGB as YUV

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
        norm_E_k_RGB *= 255
        print("Error norm RGB", norm_E_k_RGB.max(), norm_E_k_RGB.min())
        frame.write(norm_E_k_RGB, prefix + "before_", k)
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        dq_E_k = frame.read(prefix, k)
        dq_E_k = dq_E_k / 256
        dq_E_k = denorm(dq_E_k, max, min)
        dq_E_k = YUV.from_RGB(dq_E_k)
        return dq_E_k

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

def encode(video, n_frames, q_step):
    try:
        print(f"Using Q_step {q_step}")
        k = 0
        print(f"Encoding frame {k}")
        #V_k = frame.read(video, k)
        #V_k = YCoCg.from_RGB(V_k)
        #V_k_L, V_k_H = DWT.analyze_step(V_k) # (a)
        V_k_L = L.read(video, k)
        V_k_H = H.read(video, k, V_k_L.shape)
        #L.write(YCoCg.to_RGB(V_k_L), codestream, k) # (g)
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
        #frame.write(reconstructed__V_k_H, video + "reconstructed_H", k)
        L.write(reconstructed__V_k_H, video + "reconstructed_H", k)
        reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
        #quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
        #H.write(quantized_E_k_H, video, k) # (g)
        for k in range(1, n_frames):
            print(f"Encoding frame {k}")
            #V_k = frame.read(video, k)
            #V_k = YCoCg.from_RGB(V_k)
            #V_k_L, V_k_H = DWT.analyze_step(V_k) # (a)
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
            #S_k.fill(True)
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
            #IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
            IP_prediction__V_k_H = np.empty_like(prediction__V_k_H)
            for c in range(3):
                #IP_prediction__V_k_H[:,:,c] = np.zeros_like(S_k) # (E.k)
                IP_prediction__V_k_H[:,:,c] = np.where(S_k, 0, prediction__V_k_H[:,:,c]) # (E.k) Remember that we are working with coefs with 0 average.
                #IP_prediction__V_k_H[:,:,c] = np.where(S_k, 0, prediction__V_k_H[:,:,c]) # (E.k)
            #IP_prediction__V_k_H[:,:,0] = np.where(S_k, prediction__V_k_H[:,:,0], 0) # (E.k)
            #IP_prediction__V_k_H[:,:,1] = np.where(S_k, prediction__V_k_H[:,:,1], 0) # (E.k)
            #IP_prediction__V_k_H[:,:,2] = np.where(S_k, prediction__V_k_H[:,:,2], 0) # (E.k)
            #IP_prediction__V_k_H = np.zeros_like(S_k) # (E.k)
            #IP_prediction__V_k_H = prediction__V_k_H
            frame.debug_write(clip(IP_prediction__V_k_H), f"{video}encoder_IP_prediction_H_", k)
            _E_k_H = _V_k_H - IP_prediction__V_k_H[:_V_k_H.shape[0], :_V_k_H.shape[1], :] # (c)
            #assert (IP_prediction__V_k_H == 0).all()
            #assert (_E_k_H == _V_k_H).all()
            #print("IP_prediction__V_k_H.max() =", IP_prediction__V_k_H.max())
            frame.debug_write(clip(_E_k_H), f"{video}encoder_prediction_error_H_", k)
            #quantized__E_k_H = Q.quantize(_E_k_H, step=q_step) # (d)
            #dequantized__E_k_H = Q.dequantize(quantized__E_k_H, step=q_step) # (E.g)
            dequantized__E_k_H = E_codec(_E_k_H, video, k, q_step)
            #for i in range(dequantized__E_k_H.shape[0]):
            #    for j in range(dequantized__E_k_H.shape[1]):
            #        for k in range(dequantized__E_k_H.shape[2]):
            #            if dequantized__E_k_H[i,j,k] != _E_k_H[i,j,k]:
            #                print(dequantized__E_k_H[i,j,k], _E_k_H[i,j,k])
            frame.debug_write(clip(dequantized__E_k_H), f"{video}encoder_dequantized_prediction_error_H_", k)
            #assert (dequantized__E_k_H == _E_k_H.astype(np.int16)).all()
            reconstructed__V_k_H = dequantized__E_k_H + IP_prediction__V_k_H[:dequantized__E_k_H.shape[0], :dequantized__E_k_H.shape[1], :] # (E.h)
            #frame.write(reconstructed__V_k_H, video + "reconstructed_H", k) # Ojo, reconstructed__V_k_H está a 16 bits!!
            L.write(reconstructed__V_k_H, video + "reconstructed_H", k)
            #print("->", reconstructed__V_k_H.max(), reconstructed__V_k_H.min())
            #assert (reconstructed__V_k_H == _V_k_H.astype(np.int16)).all()
            frame.debug_write(clip(reconstructed__V_k_H), f"{video}encoder_reconstructed_", k)
            reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
            #quantized_E_k_H = H.reduce(quantized__E_k_H) # (f)
            #L.write(YCoCg.to_RGB(V_k_L), codestream, k) # (g)
            #L.write(V_k_L, video, k) # (g)
            #H.write(quantized_E_k_H, video, k) # (g)
    except:
        print(colors.red(f'IPP_step.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
        raise

# Unused for now
def decode(video, n_frames, q_step):       
    k = 0
    #V_k_L = YCoCg.from_RGB(L.read(codestream, k)) # (h)
    V_k_L = L.read(video, k) # (h)
    quantized_E_k_H = H.read(video, k, V_k_L.shape) # (h)
    quantized__E_k_H = H.interpolate(quantized_E_k_H) # (i)
    _V_k_L = L.interpolate(V_k_L) # (E.a)
    #assert (quantized__E_k_H.shape == _V_k_L.shape).all()
    _V_k_1_L = _V_k_L # (E.b)
    dequantized__E_k_H = Q.dequantize(quantized__E_k_H, step=q_step) # (E.g)
    reconstructed__V_k_H = dequantized__E_k_H # (E.h)
    reconstructed__V_k_1_H = reconstructed__V_k_H # (E.i)
    reconstructed_V_k_H = H.reduce(reconstructed__V_k_H) # (i)
    reconstructed_V_k = spatial_transform.synthesize_step(V_k_L, reconstructed_V_k_H) # (k)
    #reconstructed_V_k = YCoCg.to_RGB(reconstructed_V_k)
    reconstructed_V_k = np.clip(reconstructed_V_k, 0, 255).astype(np.uint8)
    frame.write(reconstructed_V_k, video, k)
    for k in range(1, n_frames):
        #V_k_L = YCoCg.from_RGB(L.read(codestream, k)) # (h)
        V_k_L = L.read(video, k) # (h)
        quantized_E_k_H = H.read(video, k, V_k_L.shape) # (h)
        quantized__E_k_H = H.interpolate(quantized_E_k_H) # (i)
        _V_k_L = L.interpolate(V_k_L) # (E.a)
        initial_flow = np.zeros((_V_k_L.shape[0], _V_k_L.shape[1], 2), dtype=np.float32)
        flow = motion.estimate(_V_k_L[:,:,0], _V_k_1_L[:,:,0], initial_flow) # (E.c)
        prediction__V_k_L = motion.make_prediction(_V_k_1_L, flow) # (E.d)
        _V_k_1_L = _V_k_L # (E.b)
        _E_k_L = _V_k_L - prediction__V_k_L # (E.e)
        S_k = _E_k_L[:,:,0] < (_V_k_L[:,:,0] - np.average(_V_k_L[:,:,0])) # (E.f)
        prediction__V_k_H = motion.make_prediction(reconstructed__V_k_1_H, flow) # (E.j)
        #IP_prediction__V_k_H = np.where(S_k, prediction__V_k_H, 0) # (E.k)
        IP_prediction__V_k_H = np.empty_like(prediction__V_k_H)
        IP_prediction__V_k_H[:,:,0] = np.where(S_k, 0, prediction__V_k_H[:,:,0]) # (E.k)
        IP_prediction__V_k_H[:,:,1] = np.where(S_k, 0, prediction__V_k_H[:,:,1]) # (E.k)
        IP_prediction__V_k_H[:,:,2] = np.where(S_k, 0, prediction__V_k_H[:,:,2]) # (E.k)
        #IP_prediction__V_k_H = np.zeros_like(S_k, dtype=np.float64) # (E.k)
        dequantized__E_k_H = Q.dequantize(quantized__E_k_H, step=q_step) # (E.g)
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
        frame.write(reconstructed_V_k, video, k)


