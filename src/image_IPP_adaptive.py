''' MRVC/image_IPP_adaptive.py '''

# An IPP video compressor, similar to image_IPP.py, but now the blocks
# can also be I-type in a B-type frame. To decide the type, we compare
# the entropy of the blocks of the residue image resulting from the
# substraction of the current frame and the current prediction frame,
# with the entropy of the blocks of the current frame. If for a given
# block the residue has a higher entropy, then the block is
# intra-coded. Only the luma is considered. I-type blocks are
# generated by discarding the corresponding prediction blocks. The
# type of each block is transmitted to the decoder.

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
#import RGB as YUV
import os
import random
import math
import image_IPP
import distortion
import values
import debug
import copy
#import sys

#image_IPP.self = sys.modules[__name__]

class image_IPP_adaptive_codec(image_IPP.image_IPP_codec):

    def encode(self, video, n_frames, q_step):
        try:
            super().encode(video, n_frames, q_step)
        except:
            print(colors.red(f'image_IPP_adaptive_codec.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise

    def create_structures(self, W_k, block_y_side, block_x_side):
        super().create_structures(W_k, block_y_side, block_x_side)
        self.block_types = np.zeros((int(W_k.shape[0]/block_y_side), int(W_k.shape[1]/block_x_side)), dtype=np.uint8)

    def decide_types(self, video, k, q_step, V_k, reconstructed_V_k, E_k, prediction_V_k, block_y_side, block_x_side, averages):
        # I/P-type block decission based on the entropy of the block.
        for y in range(int(V_k.shape[0]/block_y_side)):
            for x in range(int(V_k.shape[1]/block_x_side)):
                E_k_block_entropy = \
                    self.entropy(E_k[y*block_y_side:(y+1)*block_y_side,
                                     x*block_x_side:(x+1)*block_x_side][..., 0])
                V_k_block_entropy = \
                    self.entropy(V_k[y*block_y_side:(y+1)*block_y_side,
                                     x*block_x_side:(x+1)*block_x_side][..., 0])
                if E_k_block_entropy < V_k_block_entropy:
                    debug.print('B', end='')
                    self.block_types[y, x] = 0
                else:
                    debug.print('I', end='')
                    E_k[y*block_y_side:(y+1)*block_y_side,
                        x*block_x_side:(x+1)*block_x_side] = \
                            V_k[y*block_y_side:(y+1)*block_y_side,
                                x*block_x_side:(x+1)*block_x_side] - averages[y, x]
                    #prediction_V_k[y*block_y_side:(y+1)*block_y_side,
                    #    x*block_x_side:(x+1)*block_x_side] = 128
                    prediction_V_k[y*block_y_side:(y+1)*block_y_side,
                                   x*block_x_side:(x+1)*block_x_side] = averages[y, x]
                    self.block_types[y, x] = 1
            debug.print('')
        self.T_codec(self.block_types, video, k)

        # Regenerate the reconstructed residue using the I-type blocks
        dequantized_E_k = super().E_codec5(E_k, f"{video}texture_", k, q_step) # (g and h)

        reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1]] # (i)
        print("reconstructed_V_k", reconstructed_V_k.max(), reconstructed_V_k.min())
        return reconstructed_V_k

    def decide_types_MSE(self, video, k, q_step, V_k, reconstructed_V_k, E_k, prediction_V_k, block_y_side, block_x_side, averages):
        # I/P-type block decission based on the MSE of the block
        frame.debug_write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}all_P_", k)
        dequantized_V_k = super().I_codec(V_k, f"{video}all_I_", k, q_step)
        for y in range(int(V_k.shape[0]/block_y_side)):
            for x in range(int(V_k.shape[1]/block_x_side)):
                I_block_distortion = \
                    distortion.MSE(V_k[y*block_y_side:(y+1)*block_y_side,
                                       x*block_x_side:(x+1)*block_x_side][..., 0],
                                   dequantized_V_k[y*block_y_side:(y+1)*block_y_side,
                                                   x*block_x_side:(x+1)*block_x_side][..., 0])
                P_block_distortion = \
                    distortion.MSE(V_k[y*block_y_side:(y+1)*block_y_side,
                                       x*block_x_side:(x+1)*block_x_side][..., 0],
                                   reconstructed_V_k[y*block_y_side:(y+1)*block_y_side,
                                                     x*block_x_side:(x+1)*block_x_side][..., 0])
                #print("-->", I_block_distortion, P_block_distortion)
                if I_block_distortion > P_block_distortion:
                    debug.print('P', end='')
                    self.block_types[y, x] = 0
                else:
                    debug.print('I', end='')
                    E_k[y*block_y_side:(y+1)*block_y_side,
                        x*block_x_side:(x+1)*block_x_side] = \
                            V_k[y*block_y_side:(y+1)*block_y_side,
                                x*block_x_side:(x+1)*block_x_side] - averages[y, x]
                    prediction_V_k[y*block_y_side:(y+1)*block_y_side,
                                   x*block_x_side:(x+1)*block_x_side] = averages[y, x]
                    self.block_types[y, x] = 1
            debug.print('')

        self.T_codec(self.block_types, video, k)

        # Regenerate the reconstructed residue using the I-type blocks
        dequantized_E_k = super().E_codec5(E_k, f"{video}texture_", k, q_step) # (g and h)

        reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1]] # (i)
        print("reconstructed_V_k", reconstructed_V_k.max(), reconstructed_V_k.min())
        return reconstructed_V_k

    def compute_averages(self, V_k, block_y_side, block_x_side):
        averages = np.zeros((int(V_k.shape[0]/block_y_side),
                             int(V_k.shape[1]/block_x_side),
                             3),
                            dtype=np.int16)
        for y in range(int(V_k.shape[0]/block_y_side)):
            for x in range(int(V_k.shape[1]/block_x_side)):
                for c in range(3):
                    averages[y, x, c] = np.average(V_k[y*block_y_side:(y+1)*block_y_side,
                                                       x*block_x_side:(x+1)*block_x_side][..., c])
                debug.print(f"{averages[y, x, 0]:4d}", end='')
            print('')
        return averages

    def T_codec(self, types, prefix, frame_number):
        frame.write(types, prefix + "types_", frame_number)
        # Averages of I-type blocks?

    def compute_br(self, prefix, frames_per_second, frame_shape, n_frames):
        kbps, bpp , n_bytes = image_IPP.compute_br(prefix, frames_per_second, frame_shape, n_frames)

        # I/B-Types.
        command = f"cat {prefix}types_???.png | gzip -9 > /tmp/image_IPP_adaptive_types.gz"
        debug.print(command)
        os.system(command)
        types_length = os.path.getsize(f"/tmp/image_IPP_adaptive_types.gz")
        '''
        prev_fn = f"{prefix}types_001.png"
        types_length = os.path.getsize(prev_fn)
        for k in range(2, n_frames):
            next_fn = f"{prefix}types_{k:03d}.png"
            types_length += os.path.getsize(next_fn)
            counter = -2
            with open(prev_fn, "rb") as prev_f, open(next_fn, "rb") as next_f:
                while True:
                    prev_byte = prev_f.read(1)
                    next_byte = next_f.read(1)
                    if prev_byte != next_byte:
                        break
                    if prev_byte == b'':
                        break
                    if next_byte == b'':
                        break
                    counter += 1
            types_length -= counter
        '''
        frame_height = frame_shape[0]
        frame_width = frame_shape[1]
        n_channels = frame_shape[2]
        sequence_time = n_frames/frames_per_second
        types_kbps = types_length*8/sequence_time/1000
        types_bpp = types_length*8/(frame_width*frame_height*n_channels*n_frames)
        print(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")
        print(f"types: {types_length} bytes, {types_kbps} KBPS, {types_bpp} BPP")
        return kbps + types_kbps, bpp + types_bpp, types_length + n_bytes

    def entropy(self, sequence_of_symbols):
        '''In bits/symbol.'''
        value, counts = np.unique(sequence_of_symbols, return_counts = True)
        probs = counts / len(sequence_of_symbols)
        n_classes = np.count_nonzero(probs)

        if n_classes <= 1:
            return 0

        entropy = 0.
        for i in probs:
            entropy -= i * math.log(i, 2)

        return entropy

    def norm(x):
        return (frame.normalize(x)*255).astype(np.uint8)

    def _clip(x):
        return(np.clip(x, 0 ,255).astype(np.uint8))

    def _I_codec(E_k, prefix, k, q_step):
        print("Error", E_k.max(), E_k.min())
        #frame.write(YUV.to_RGB(E_k), prefix + "before_", k)
        to_write = YUV.to_RGB(V_k).astype(np.uint8)
        frame.write(YUV.to_RGB(E_k) + 128, prefix + "before_", k)
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} {prefix}{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        #dq_E_k = (YUV.from_RGB(frame.read(prefix, k)))
        dq_E_k = (YUV.from_RGB(frame.read(prefix, k) - 128))
        return dq_E_k

    def _I_codec2(E_k, prefix, k, q_step):
        print("Error", E_k.max(), E_k.min())
        frame.write(YUV.to_RGB(E_k) + 128, prefix + "before_", k)
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -b 64k {prefix}{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        dq_E_k = (YUV.from_RGB(frame.read(prefix, k) - 128))
        return dq_E_k

    def _E_codec4(E_k, prefix, k, q_step):
        print("Error", E_k.max(), E_k.min(), q_step)
        #frame.write(YUV.to_RGB(E_k), prefix + "before_", k)
        #frame.write(YUV.to_RGB(E_k) + 128, prefix + "before_", k)
        # Clipping ... is more efficient than quantizing.
        out = clip(YUV.to_RGB(E_k) + 128)
        # Quantizing
        #out = YUV.to_RGB(E_k)//2 + 128
        # Normalizing
        #out, max, min = values.norm(YUV.to_RGB(E_k)); out *= 255
        print("Error out ", out.max(), out.min()) 
        frame.write(out, prefix + "before_", k)
        #frame.write(clip(YUV.to_RGB(E_k)), prefix + "before_", k)
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        #dq_E_k = YUV.from_RGB(frame.read(prefix, k))
        # De-clipping
        dq_E_k = YUV.from_RGB(frame.read(prefix, k) - 128)*1
        # De-quantizing
        #dq_E_k = YUV.from_RGB(frame.read(prefix, k) - 128)*2
        # De-normalizing
        #dq_E_k = YUV.from_RGB(values.denorm(frame.read(prefix, k)/255, max, min))
        #dq_E_k = YUV.from_RGB(frame.read(prefix, k))
        return dq_E_k

    def _E_codec5(E_k, prefix, k, q_step):
        print("Error", E_k.max(), E_k.min())
        frame.write(clip(YUV.to_RGB(E_k) + 128), prefix + "before_", k)
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -b 64k -flags -loop {prefix}{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        dq_E_k = YUV.from_RGB(frame.read(prefix, k) - 128)
        return dq_E_k

    def _V_codec(motion, n_levels, prefix, frame_number):
        #print(prefix+"_y")
        pyramid = LP.analyze(motion, n_levels)
        #pyramid[0][:,:,:] = 0
        frame.write(pyramid[0][...,0], prefix + "y_", frame_number)
        frame.write(pyramid[0][...,1], prefix + "x_", frame_number)
        for resolution in pyramid[1:]:
            resolution[...] = 0
        reconstructed_motion = LP.synthesize(pyramid, n_levels)
        #print(motion-reconstructed_motion[:motion.shape[0], :motion.shape[1], :])
        return np.rint(reconstructed_motion).astype(np.int16)
        #return reconstructed_motion.astype(np.int16)
        #decom_Y = pywt.wavedec2(motion[:,:,0], 'db1', mode='per', levels=3)
        #decom_X = pywt.wavedec2(motion[:,:,1], 'db1', mode='per', levels=3)
        #L.write(decom_Y[0], prefix, k)
        #L.write(decom_Y[1], prefix, k)
        #H_subbands_decom_Y = decom_Y[1:]
        #for resolution in H_subbands_decom_Y:
        #    resolution[0][:,:] = 0
        #    resolution[1][:,:] = 0
        #    resolution[2][:,:] = 0
        #H_subbands_decom_X = decom_X[1:]
        #for resolution in H_subbands_decom_X:
        #    resolution[0][:,:] = 0
        #    resolution[1][:,:] = 0
        #    resolution[2][:,:] = 0
        #pywt.waverec2(decom_Y, 'db1')
        #pywt.waverec2(decom_X, 'db1')
        #_motion = np.empty_like(motion)
        #_motion[:,:,0] = decom_Y[:,:]
        #_motion[:,:,0] = decom_X[:,:]
        #return _motion

    def _V_codec(motion, n_levels, prefix, frame_number):
        pyramid = np.rint(motion).astype(np.int16)
        frame.write(pyramid[:,:,0], prefix+"_y_", frame_number)
        frame.write(pyramid[:,:,1], prefix+"_x_", frame_number)
        return pyramid

    def _substract_averages(V_k, averages):
        for y in range(int(V_k.shape[0]/block_y_side)):
            for x in range(int(V_k.shape[1]/block_x_side)):
                for c in range(3):
                    V_k[y*block_y_side:(y+1)*block_y_side,
                        x*block_x_side:(x+1)*block_x_side][..., c] -= averages[y, x, c]
        return V_k

    def _add_averages(V_k, averages):
        for y in range(int(V_k.shape[0]/block_y_side)):
            for x in range(int(V_k.shape[1]/block_x_side)):
                for c in range(3):
                    V_k[y*block_y_side:(y+1)*block_y_side,
                        x*block_x_side:(x+1)*block_x_side][..., c] += averages[y, x, c]
        return V_k

    def _encode(video, n_frames, q_step):
        try:
            k = 0
            W_k = frame.read(video, k).astype(np.int16)
            create_structures(W_k)
            #averages = compute_averages(W_k)
            #W_k = substract_averages(W_k, averages)
            #flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)

            V_k = YUV.from_RGB(W_k) # (a)
            #block_types = np.zeros((int(V_k.shape[0]/block_y_side), int(V_k.shape[1]/block_x_side)), dtype=np.uint8)
            V_k_1 = V_k # (b)
            E_k = V_k # (f)
            dequantized_E_k = image_IPP.I_codec(V_k, f"{video}texture_", 0, q_step) # (g and h) # Mismo que E_codec4!!!!
            reconstructed_V_k = dequantized_E_k # (i)
            #frame.debug_write(clip(add_averages(YUV.to_RGB(reconstructed_V_k), averages)),
            #                       f"{video}reconstructed_", k) # Decoder's output
            frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (j)
            for k in range(1, n_frames):
                W_k = frame.read(video, k).astype(np.int16)
                #W_k = substract_averages(W_k, averages)
                V_k = YUV.from_RGB(W_k) # (a)
                #averages = compute_averages(V_k)
                compute_averages(V_k)
                #initial_flow = np.zeros((V_k.shape[0], V_k.shape[1], 2), dtype=np.float32)
                flow = motion.estimate(V_k[...,0], V_k_1[...,0], image_IPP.initial_flow) # (c)
                print("COMPUTED flow", flow.max(), flow.min())
                V_k_1 = V_k # (b)
                reconstructed_flow = V_codec(flow, LOG2_BLOCK_SIDE, f"{video}motion_", k) # (d and e)
                print("USED flow", reconstructed_flow.max(), reconstructed_flow.min())
                prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow) # (j)
                frame.debug_write(clip(YUV.to_RGB(prediction_V_k)), f"{video}prediction_", k) # Decoder's output
                E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
                print("V_k", V_k.max(), V_k.min())
                print("prediction_V_k", prediction_V_k.max(), prediction_V_k.min())
                print("E_k", E_k.max(), E_k.min())
                #E_k = np.clip(E_k, -128, 127) # No necesario si 16bpp
                #dequantized_E_k = E_codec4(E_k, f"{video}texture_", k, q_step) # (g and h)
                dequantized_E_k = image_IPP.E_codec5(E_k, f"{video}texture_", k, q_step) # (g and h)

                print("dequantized_E_k", dequantized_E_k.max(), dequantized_E_k.min())
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1]] # (i)
                print("--> reconstructed_V_k", reconstructed_V_k.max(), reconstructed_V_k.min())
                frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_without_I_", k) # Decoder's output
                reconstructed_V_k = decide_types(video, k, q_step, V_k, reconstructed_V_k, E_k, prediction_V_k)
                frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
                reconstructed_V_k_1 = reconstructed_V_k # (j)
        except:
            print(colors.red(f'image_IPP_adaptive.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise

    def _encode5(video, n_frames, q_step):
        try:
            k = 0
            W_k = frame.read(video, k)
            averages = compute_averages(W_k)
            W_k = substract_averages(W_k, averages)
            flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)
            V_k = YUV.from_RGB(W_k) # (a)
            block_types = np.zeros((int(V_k.shape[0]/block_y_side), int(V_k.shape[1]/block_x_side)), dtype=np.uint8)
            V_k_1 = V_k.copy() # (b)
            E_k = V_k.copy() # (f)
            dequantized_E_k = I_codec(E_k, f"{video}texture_", 0, q_step) # (g and h) # Mismo que E_codec4!!!!
            reconstructed_V_k = dequantized_E_k # (i)
            frame.debug_write(clip(add_averages(YUV.to_RGB(reconstructed_V_k), averages)),
                                   f"{video}reconstructed_", k) # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (j)
            for k in range(1, n_frames):
                W_k = frame.read(video, k)
                averages = compute_averages(W_k)
                W_k = substract_averages(W_k, averages)
                V_k = YUV.from_RGB(W_k) # (a)
                initial_flow = np.zeros((V_k.shape[0], V_k.shape[1], 2), dtype=np.float32)
                flow = motion.estimate(V_k[...,0], V_k_1[...,0], initial_flow) # (c)
                print("COMPUTED flow", flow.max(), flow.min())
                V_k_1 = V_k.copy() # (b)
                reconstructed_flow = V_codec(flow, LOG2_BLOCK_SIDE, f"{video}motion_", k) # (d and e)
                print("USED flow", reconstructed_flow.max(), reconstructed_flow.min())
                prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow) # (j)
                E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
                print("V_k", V_k.max(), V_k.min())
                print("prediction_V_k", prediction_V_k.max(), prediction_V_k.min())
                print("E_k", E_k.max(), E_k.min())
                E_k = np.clip(E_k, -128, 127)
                dequantized_E_k = E_codec5(E_k, f"{video}texture_", k, q_step) # (g and h)

                print("dequantized_E_k", dequantized_E_k.max(), dequantized_E_k.min())
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1]] # (i)
                print("reconstructed_V_k", reconstructed_V_k.max(), reconstructed_V_k.min())
                frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k) + 128), f"{video}reconstructed_", k) # Decoder's output
                dequantized_V_k = I_codec2(V_k, f"{video}texture_", k, q_step)
                for y in range(int(V_k.shape[0]/block_y_side)):
                    for x in range(int(V_k.shape[1]/block_x_side)):
                        V_k_block_distortion = \
                            distortion.MSE(V_k[y*block_y_side:(y+1)*block_y_side,
                                               x*block_x_side:(x+1)*block_x_side][..., 0],
                                           dequantized_V_k[y*block_y_side:(y+1)*block_y_side,
                                                           x*block_x_side:(x+1)*block_x_side][..., 0])
                        reconstructed_V_k_block_distortion = \
                            distortion.MSE(V_k[y*block_y_side:(y+1)*block_y_side,
                                               x*block_x_side:(x+1)*block_x_side][..., 0],
                                           reconstructed_V_k[y*block_y_side:(y+1)*block_y_side,
                                                             x*block_x_side:(x+1)*block_x_side][..., 0])
                        if V_k_block_distortion > reconstructed_V_k_block_distortion:
                            print('B', end='')
                            block_types[y, x] = 0
                        else:
                            print('I', end='')
                            E_k[y*block_y_side:(y+1)*block_y_side,
                                x*block_x_side:(x+1)*block_x_side] = \
                                    V_k[y*block_y_side:(y+1)*block_y_side,
                                        x*block_x_side:(x+1)*block_x_side]
                            #prediction_V_k[y*block_y_side:(y+1)*block_y_side,
                            #    x*block_x_side:(x+1)*block_x_side] = 128
                            prediction_V_k[y*block_y_side:(y+1)*block_y_side,
                                           x*block_x_side:(x+1)*block_x_side] = 0
                            block_types[y, x] = 1
                    print('')
                T_codec(block_types, video, k)
                E_k = np.clip(E_k, -128, 127)
                dequantized_E_k = E_codec4(E_k, f"{video}texture_", k, q_step) # (g and h)

                print("dequantized_E_k", dequantized_E_k.max(), dequantized_E_k.min())
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1]] # (i)
                print("reconstructed_V_k", reconstructed_V_k.max(), reconstructed_V_k.min())
                frame.debug_write(clip(add_averages(YUV.to_RGB(reconstructed_V_k), averages)),
                                  f"{video}reconstructed_", k) # Decoder's output

                reconstructed_V_k_1 = reconstructed_V_k # (j)
        except:
            print(colors.red(f'image_IPP_step.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise

    def _encode2(video, n_frames, q_step):
        try:
            k = 0
            #W_k = frame.read(video, k)
            W_k = frame.read(video, k) - 128
            flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)
            V_k = YUV.from_RGB(W_k) # (a)
            block_types = np.zeros((int(V_k.shape[0]/block_y_side), int(V_k.shape[1]/block_x_side)), dtype=np.uint8)
            V_k_1 = V_k.copy() # (b)
            E_k = V_k.copy() # (f)
            dequantized_E_k = I_codec(E_k, f"{video}texture_", 0, q_step) # (g and h) # Mismo que E_codec4!!!!
            reconstructed_V_k = dequantized_E_k # (i)
            #frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
            frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k) + 128), f"{video}reconstructed_", k) # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (j)
            for k in range(1, n_frames):
                #W_k = frame.read(video, k)
                W_k = frame.read(video, k) - 128
                V_k = YUV.from_RGB(W_k) # (a)
                initial_flow = np.zeros((V_k.shape[0], V_k.shape[1], 2), dtype=np.float32)
                flow = motion.estimate(V_k[...,0], V_k_1[...,0], initial_flow) # (c)
                print("COMPUTED flow", flow.max(), flow.min())
                V_k_1 = V_k.copy() # (b)
                reconstructed_flow = V_codec(flow, LOG2_BLOCK_SIDE, f"{video}motion_", k) # (d and e)
                print("USED flow", reconstructed_flow.max(), reconstructed_flow.min())
                #frame.debug_write(motion.colorize(flow), f"{codestream}flow", k)
                #frame.debug_write(motion.colorize(reconstructed_flow.astype(np.float32)), f"{codestream}reconstructed_flow", k)
                #print("reconstructed_V_k_1", reconstructed_V_k_1.max(), reconstructed_V_k_1.min())
                prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow) # (j)
                #frame.debug_write(clip(YUV.to_RGB(prediction_V_k)), f"{codestream}encoder_prediction", k)
                E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
                #E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] - 128 # (f)
                print("V_k", V_k.max(), V_k.min())
                print("prediction_V_k", prediction_V_k.max(), prediction_V_k.min())
                print("E_k", E_k.max(), E_k.min())

                for y in range(int(V_k.shape[0]/block_y_side)):
                    for x in range(int(V_k.shape[1]/block_x_side)):
                        E_k_block_entropy = \
                            entropy(E_k[y*block_y_side:(y+1)*block_y_side,
                                        x*block_x_side:(x+1)*block_x_side][..., 0])
                        V_k_block_entropy = \
                            entropy(V_k[y*block_y_side:(y+1)*block_y_side,
                                        x*block_x_side:(x+1)*block_x_side][..., 0])
                        if E_k_block_entropy < V_k_block_entropy:
                            print('B', end='')
                            block_types[y, x] = 0
                        else:
                            print('I', end='')
                            E_k[y*block_y_side:(y+1)*block_y_side,
                                x*block_x_side:(x+1)*block_x_side] = \
                                    V_k[y*block_y_side:(y+1)*block_y_side,
                                        x*block_x_side:(x+1)*block_x_side]
                            #prediction_V_k[y*block_y_side:(y+1)*block_y_side,
                            #    x*block_x_side:(x+1)*block_x_side] = 128
                            prediction_V_k[y*block_y_side:(y+1)*block_y_side,
                                x*block_x_side:(x+1)*block_x_side] = 0
                            block_types[y, x] = 1
                    print('')
                T_codec(block_types, video, k)

                #E_k = np.clip(E_k, 0, 255)
                E_k = np.clip(E_k, -128, 127)

                #frame.debug_write(clip(YUV.to_RGB(E_k)+128), f"{codestream}encoder_prediction_error", k)
                dequantized_E_k = E_codec4(E_k, f"{video}texture_", k, q_step) # (g and h)
                print("dequantized_E_k", dequantized_E_k.max(), dequantized_E_k.min())
                #frame.debug_write(clip(YUV.to_RGB(dequantized_E_k)), f"{codestream}encoder_dequantized_prediction_error", k)
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1]] # (i)
                print("reconstructed_V_k", reconstructed_V_k.max(), reconstructed_V_k.min())
                #reconstructed_V_k -= 128
                #reconstructed_V_k = np.clip(reconstructed_V_k, 0, 255)
                frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
                reconstructed_V_k_1 = reconstructed_V_k # (j)
        except:
            print(colors.red(f'image_IPP_step.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise

    def _encode3(video, n_frames, q_step):
        try:
            k = 0
            W_k = frame.read(video, k) - 128
            flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)
            V_k = YUV.from_RGB(W_k) # (a)
            block_types = np.zeros((int(V_k.shape[0]/block_y_side), int(V_k.shape[1]/block_x_side)), dtype=np.uint8)
            V_k_1 = V_k.copy() # (b)
            E_k = V_k.copy() # (f)
            dequantized_E_k = I_codec(E_k, f"{video}texture_", 0, q_step) # (g and h) # Mismo que E_codec4!!!!
            reconstructed_V_k = dequantized_E_k # (i)
            frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k) + 128), f"{video}reconstructed_", k) # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (j)
            for k in range(1, n_frames):
                W_k = frame.read(video, k) - 128
                V_k = YUV.from_RGB(W_k) # (a)
                initial_flow = np.zeros((V_k.shape[0], V_k.shape[1], 2), dtype=np.float32)
                flow = motion.estimate(V_k[...,0], V_k_1[...,0], initial_flow) # (c)
                print("COMPUTED flow", flow.max(), flow.min())
                V_k_1 = V_k.copy() # (b)
                reconstructed_flow = V_codec(flow, LOG2_BLOCK_SIDE, f"{video}motion_", k) # (d and e)
                print("USED flow", reconstructed_flow.max(), reconstructed_flow.min())
                prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow) # (j)
                E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
                print("V_k", V_k.max(), V_k.min())
                print("prediction_V_k", prediction_V_k.max(), prediction_V_k.min())
                print("E_k", E_k.max(), E_k.min())
                E_k = np.clip(E_k, -128, 127)
                dequantized_E_k = E_codec4(E_k, f"{video}texture_", k, q_step) # (g and h)

                print("dequantized_E_k", dequantized_E_k.max(), dequantized_E_k.min())
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1]] # (i)
                print("reconstructed_V_k", reconstructed_V_k.max(), reconstructed_V_k.min())
                frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k) + 128), f"{video}reconstructed_", k) # Decoder's output
                dequantized_V_k = I_codec(V_k, f"{video}texture_", k, q_step)
                for y in range(int(V_k.shape[0]/block_y_side)):
                    for x in range(int(V_k.shape[1]/block_x_side)):
                        V_k_block_distortion = \
                            distortion.MSE(V_k[y*block_y_side:(y+1)*block_y_side,
                                               x*block_x_side:(x+1)*block_x_side][..., 0],
                                           dequantized_V_k[y*block_y_side:(y+1)*block_y_side,
                                                           x*block_x_side:(x+1)*block_x_side][..., 0])
                        reconstructed_V_k_block_distortion = \
                            distortion.MSE(V_k[y*block_y_side:(y+1)*block_y_side,
                                               x*block_x_side:(x+1)*block_x_side][..., 0],
                                           reconstructed_V_k[y*block_y_side:(y+1)*block_y_side,
                                                             x*block_x_side:(x+1)*block_x_side][..., 0])
                        if V_k_block_distortion > reconstructed_V_k_block_distortion:
                            print('B', end='')
                            block_types[y, x] = 0
                        else:
                            print('I', end='')
                            E_k[y*block_y_side:(y+1)*block_y_side,
                                x*block_x_side:(x+1)*block_x_side] = \
                                    V_k[y*block_y_side:(y+1)*block_y_side,
                                        x*block_x_side:(x+1)*block_x_side]
                            #prediction_V_k[y*block_y_side:(y+1)*block_y_side,
                            #    x*block_x_side:(x+1)*block_x_side] = 128
                            prediction_V_k[y*block_y_side:(y+1)*block_y_side,
                                           x*block_x_side:(x+1)*block_x_side] = 0
                            block_types[y, x] = 1
                    print('')
                T_codec(block_types, video, k)
                E_k = np.clip(E_k, -128, 127)
                dequantized_E_k = E_codec4(E_k, f"{video}texture_", k, q_step) # (g and h)

                print("dequantized_E_k", dequantized_E_k.max(), dequantized_E_k.min())
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1]] # (i)
                print("reconstructed_V_k", reconstructed_V_k.max(), reconstructed_V_k.min())
                frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k) + 128), f"{video}reconstructed_", k) # Decoder's output
                reconstructed_V_k_1 = reconstructed_V_k # (j)
        except:
            print(colors.red(f'image_IPP_step.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise

    def _compute_br2(prefix, frames_per_second, frame_shape, n_frames):
        #print("*"*80, prefix)
        #os.system(f"ffmpeg -y -i {prefix}_from_mp4_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_texture.mp4")
        #os.system(f"ffmpeg -f concat -safe 0 -i <(for f in {prefix}_*.mp4; do echo \"file '$PWD/$f'\"; done) -c copy /tmp/image_IPP_texture.mp4")
        command = f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {prefix}codestream_*.mp4; do echo \"file '$f'\"; done) -c copy /tmp/image_IPP_texture.mp4"
        print(command)
        os.system(command)
        #print(f"ffmpeg -loglevel fatal -y -i {prefix}motion_y_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_motion_y.mp4")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}motion_y_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_motion_y.mp4"
        print(command)
        os.system(command)
        command = f"ffmpeg -loglevel fatal -y -i {prefix}motion_x_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_motion_x.mp4"
        print(command)
        os.system(command)
        command = f"ffmpeg -loglevel fatal -y -i {prefix}types_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_types.mp4"
        print(command)
        os.system(command)

        frame_height = frame_shape[0]
        frame_width = frame_shape[1]
        n_channels = frame_shape[2]
        sequence_time = n_frames/frames_per_second
        print(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")

        texture_bytes = os.path.getsize("/tmp/image_IPP_texture.mp4")
        total_bytes = texture_bytes
        kbps = texture_bytes*8/sequence_time/1000
        bpp = texture_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        print(f"texture: {texture_bytes} bytes, {kbps} KBPS, {bpp} BPP")

        motion_y_bytes = os.path.getsize("/tmp/image_IPP_motion_y.mp4")
        total_bytes += motion_y_bytes
        kbps = motion_y_bytes*8/sequence_time/1000
        print(f"motion (Y direction): {motion_y_bytes} bytes, {kbps} KBPS")

        motion_x_bytes = os.path.getsize("/tmp/image_IPP_motion_x.mp4")
        total_bytes += motion_x_bytes
        kbps = motion_x_bytes*8/sequence_time/1000
        print(f"motion (X direction): {motion_x_bytes} bytes, {kbps} KBPS")

        types_bytes = os.path.getsize("/tmp/image_IPP_types.mp4")
        total_bytes += types_bytes
        kbps = types_bytes*8/sequence_time/1000
        print(f"block types: {types_bytes} bytes, {kbps} KBPS")

        kbps = total_bytes*8/sequence_time/1000
        bpp = total_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        #print(f"total: {kbps} KBPS, {bpp} BPP")

        return kbps, bpp

codec = image_IPP_adaptive_codec()
def encode(video, n_frames, q_step):
    codec.encode(video, n_frames, q_step)

def compute_br(prefix, frames_per_second, frame_shape, n_frames):
    return codec.compute_br(prefix, frames_per_second, frame_shape, n_frames)
