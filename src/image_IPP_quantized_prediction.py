''' MRVC/image_IPP_quantized_prediction.py '''

# The prediction is quantized to mininize the entropy of the residue.

import DWT
import LP
import numpy as np
import L_DWT as L
import H_DWT as H
import deadzone_quantizer as Q
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
from scipy.fftpack import dct

class image_IPP_quantized_prediction_codec(image_IPP.image_IPP_codec):

    def _encode(self, video, first_frame, n_frames, q_step):
        try:
            k = 0
            W_k = frame.read(video, k).astype(np.int16)
            initial_flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)
            blocks_in_y = int(W_k.shape[0]/self.block_y_side)
            blocks_in_x = int(W_k.shape[1]/self.block_x_side)
            predicted_block_Q_step = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=1, dtype=np.uint8)
            V_k = YUV.from_RGB(W_k) # (a)
            V_k_1 = V_k # (b)
            E_k = V_k # (f)
            dequantized_E_k = self.I_codec(V_k, f"{video}texture_", 0, q_step) # (g and h)
            reconstructed_V_k = dequantized_E_k # (i)
            frame.write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (j)
            for k in range(1, n_frames):
                W_k = frame.read(video, k).astype(np.int16)
                V_k = YUV.from_RGB(W_k) # (a)
                flow = motion.estimate(V_k[...,0], V_k_1[...,0], initial_flow) # (c)
                V_k_1 = V_k # (b)
                reconstructed_flow = self.V_codec(flow, self.log2_block_side, f"{video}motion_", k) # (d and e)
                prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow) # (j)
                min_block_MSE = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=999999, dtype=np.float32)

                # Optimize pred_q_step for each block in prediction_V_k by
                # minimizing the distortion of the reconstruction
                for y in range(blocks_in_y):
                    for x in range(blocks_in_x):
                        for pred_q_step in range(1, 256):
                            predicted_block = V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                  x*self.block_x_side:(x+1)*self.block_x_side]
                            prediction_block = prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                              x*self.block_x_side:(x+1)*self.block_x_side]
                            quantized_prediction_block = Q.quantize(prediction_block, pred_q_step)
                            residue_block = predicted_block - quantized_prediction_block
                            dequantized_block_residue = self.E_codec4(residue_block, f"/tmp/block", y*blocks_in_x+x, q_step)
                            reconstructed_block = dequantized_block_residue + prediction_block
                            block_MSE = distortion.MSE(predicted_block[..., 0], reconstructed_block[..., 0])
                            #print(f"block_MSE={block_MSE} min_block_MSE[{y}][{x}]={min_block_MSE[y][x]}")
                            if block_MSE < min_block_MSE[y][x]:
                                min_block_MSE[y][x] = block_MSE
                                predicted_block_Q_step[y][x] = pred_q_step
                            else:
                                break
                        print(predicted_block_Q_step[y][x], end=' ')
                    print()
                self.T_codec(predicted_block_Q_step, video, k)
                print("---------------")

                # Build the quantized prediction (for all components)
                for y in range(blocks_in_y):
                    for x in range(blocks_in_x):
                        prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                       x*self.block_x_side:(x+1)*self.block_x_side] = \
                        Q.quantize(prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                  x*self.block_x_side:(x+1)*self.block_x_side], predicted_block_Q_step[y][x])

                frame.debug_write(self.clip(YUV.to_RGB(prediction_V_k)), f"{video}prediction_", k)
                E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
                frame.debug_write(self.clip(YUV.to_RGB(E_k)+128), f"{video}prediction_error_", k)
                dequantized_E_k = self.E_codec4(E_k, f"{video}texture_", k, q_step) # (g and h)
                frame.debug_write(self.clip(YUV.to_RGB(dequantized_E_k) + 128), f"{video}dequantized_prediction_error_", k)
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1], :] # (i)
                frame.write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
                reconstructed_V_k_1 = reconstructed_V_k # (j)
                            
        except:
            print(colors.red(f'image_IPP_adaptive_codec.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise

    def encode(self, video, first_frame, n_frames, q_step):
        try:
            k = first_frame
            W_k = frame.read(video, k).astype(np.int16)
            initial_flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)
            blocks_in_y = int(W_k.shape[0]/self.block_y_side)
            blocks_in_x = int(W_k.shape[1]/self.block_x_side)
            predicted_block_Q_step = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=1, dtype=np.uint8)
            V_k = YUV.from_RGB(W_k) # (a)
            V_k_1 = V_k # (b)
            E_k = V_k # (f)
            dequantized_E_k = self.I_codec(V_k, f"{video}texture_", 0, q_step) # (g and h)
            reconstructed_V_k = dequantized_E_k # (i)
            frame.write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (j)
            for k in range(first_frame + 1, first_frame + n_frames):
                W_k = frame.read(video, k).astype(np.int16)
                V_k = YUV.from_RGB(W_k) # (a)
                flow = motion.estimate(V_k[...,0], V_k_1[...,0], initial_flow) # (c)
                V_k_1 = V_k # (b)
                reconstructed_flow = self.V_codec(flow, self.log2_block_side, f"{video}motion_", k) # (d and e)
                prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow) # (j)
                min_E_k_block_entropy = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=8, dtype=np.float32)

                # Optimize q_step for each block in prediction_V_k by
                # minimizing the entropy of the residue
                for y in range(blocks_in_y):
                    for x in range(blocks_in_x):
                        for pred_q_step in range(1, 256):
                            E_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                x*self.block_x_side:(x+1)*self.block_x_side][..., 0] = \
                                    V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                        x*self.block_x_side:(x+1)*self.block_x_side][..., 0] - \
                                        Q.quantize(prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                                     x*self.block_x_side:(x+1)*self.block_x_side][..., 0], pred_q_step)
                            E_k_block_entropy = self.entropy(E_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                                 x*self.block_x_side:(x+1)*self.block_x_side][..., 0])
                            if E_k_block_entropy < min_E_k_block_entropy[y][x]:
                                min_E_k_block_entropy[y][x] = E_k_block_entropy
                                predicted_block_Q_step[y][x] = pred_q_step
                            else:
                                break
                        print(predicted_block_Q_step[y][x], end=' ')
                    print()
                self.T_codec(predicted_block_Q_step, video, k)
                print()

                # Build the quantized prediction (for all components)
                for y in range(blocks_in_y):
                    for x in range(blocks_in_x):
                        prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                       x*self.block_x_side:(x+1)*self.block_x_side] = \
                        Q.quantize(prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                  x*self.block_x_side:(x+1)*self.block_x_side], predicted_block_Q_step[y][x])
                        if predicted_block_Q_step[y][x] == 2:
                            prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                       x*self.block_x_side:(x+1)*self.block_x_side] += 32#64
                        if predicted_block_Q_step[y][x] == 3:
                            prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                       x*self.block_x_side:(x+1)*self.block_x_side] += 64#72
                        if predicted_block_Q_step[y][x] == 4:
                            prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                       x*self.block_x_side:(x+1)*self.block_x_side] += 72#80

                        #+ 128 - 128 >> (predicted_block_Q_step[y][x] - 1) 

                frame.debug_write(self.clip(YUV.to_RGB(prediction_V_k)), f"{video}prediction_", k)
                E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
                frame.debug_write(self.clip(YUV.to_RGB(E_k)+128), f"{video}prediction_error_", k)
                dequantized_E_k = self.E_codec4(E_k, f"{video}texture_", k, q_step) # (g and h)
                frame.debug_write(self.clip(YUV.to_RGB(dequantized_E_k) + 128), f"{video}dequantized_prediction_error_", k)
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1], :] # (i)
                frame.write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
                reconstructed_V_k_1 = reconstructed_V_k # (j)
                            
        except:
            print(colors.red(f'image_IPP_adaptive_codec.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise

    def T_codec(self, types, prefix, frame_number):
        frame.write(types, prefix + "types_", frame_number)

    def compute_br(self, prefix, frames_per_second, frame_shape, first_frame, n_frames):
        kbps, bpp , n_bytes = image_IPP.compute_br(prefix, frames_per_second, frame_shape, first_frame, n_frames)

        # I/B-Types.
        command = f"cat {prefix}types_???.png | gzip -9 > /tmp/image_IPP_adaptive_types.gz"
        debug.print(command)
        os.system(command)
        types_length = os.path.getsize(f"/tmp/image_IPP_adaptive_types.gz")
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
        probs = counts / np.size(sequence_of_symbols)
        n_classes = np.count_nonzero(probs)

        if n_classes <= 1:
            return 0

        entropy = 0.
        for i in probs:
            entropy -= i * math.log(i, 2)

        return entropy

codec = image_IPP_quantized_prediction_codec()
def encode(video, first_frame, n_frames, q_step):
    codec.encode(video, first_frame, n_frames, q_step)

def compute_br(prefix, frames_per_second, frame_shape, first_frame, n_frames):
    return codec.compute_br(prefix, frames_per_second, frame_shape, first_frame, n_frames)
