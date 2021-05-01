''' MRVC/image_IPP_quantized_residue.py '''

# The residue is quantized to mininize the distortion of the reconstruction. No I-blocks in P-frames.

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
from scipy.fftpack import dct, idct
import information

class image_IPP_quantized_residue_codec(image_IPP.image_IPP_codec):

    def encode(self, video, n_frames, q_step):
        try:
            k = 0
            W_k = frame.read(video, k).astype(np.int16)
            initial_flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)
            blocks_in_y = int(W_k.shape[0]/self.block_y_side)
            blocks_in_x = int(W_k.shape[1]/self.block_x_side)
            block_Q_step = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=q_step, dtype=np.uint8)
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
                block_RD_slope = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=0, dtype=np.float32)

                # For each block, find a block_q_step to use the same
                # RD slope for all blocks after quantization of the
                # residue.

                def QDCT(block, q_step):
                    '''Deadzone quantization in the DCT domain. <block> is the data and <Q_step> the quantization step.''' 
                    DCT_block = dct(block)
                    dequantized_DCT_block = Q.quan_dequan(block, q_step)
                    dequantized_block = idct(dequantized_DCT_block)
                    return dequantized_block

                def compute_block_slope(V_k, prediction_V_k, q_step):
                    '''Compute the RD slope of a block for the quantization step <q_step>.'''
                    predicted_block = V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                          x*self.block_x_side:(x+1)*self.block_x_side]
                    prediction_block = prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                      x*self.block_x_side:(x+1)*self.block_x_side]
                    residue_block = predicted_block - prediction_block
                    RD_point_for_Q_step_one = (information.entropy(residue_block), 0)
                    dequantized_residue_block = QDCT(residue_block, q_step)
                    reconstructed_block = dequantized_residue_block + prediction_block
                    current_RD_point = (information.entropy(dequantized_residue_block), distortion.MSE(predicted_block, reconstructed_block))
                    block_RD_slope = (RD_point_for_Q_step_one[0] - current_RD_point[0]) / current_RD_point[1]
                    return block_RD_slope

                # Compute the current slopes
                for y in range(blocks_in_y):
                    for x in range(blocks_in_x):
                        block_RD_slope[y][x] = compute_block_slope(V_k, prediction_V_k, q_step)

                # Find the lower slope
                #min_RD_slope = np.unravel_index(np.argmin(block_RD_slope, axis=None), block_RD_slope.shape)

                min_RD_slope = np.min(block_RD_slope)

                # Decrease the slope of those blocks with a slope higher the smaller one(s)
                for y in range(blocks_in_y):
                    for x in range(blocks_in_x):
                        if block_RD_slope[y][x] > min_RD_slope:
                            next_Q_step = block_Q_step[y][x] - 1
                            block_RD_slope[y][x] = compute_block_slope(V_k, prediction_V_k, next_Q_step)
                            block_Q_step[y][x] = next_Q_step

                # At this point, all residue blocks must have the same slope 
                self.T_codec(block_Q_step, video, k)

                frame.debug_write(self.clip(YUV.to_RGB(prediction_V_k)), f"{video}prediction_", k)
                E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
                frame.debug_write(self.clip(YUV.to_RGB(E_k)+128), f"{video}prediction_error_", k)
                for y in range(blocks_in_y):
                    for x in range(blocks_in_x):
                        dequantized_E_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                        x*self.block_x_side:(x+1)*self.block_x_side] = \
                        QDCT(E_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                 x*self.block_x_side:(x+1)*self.block_x_side], block_Q_step[y][x])
                self.E_codec4(dequantized_E_k, f"{video}texture_", k, 1) # (g and h)

                frame.debug_write(self.clip(YUV.to_RGB(dequantized_E_k) + 128), f"{video}dequantized_prediction_error_", k)
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1], :] # (i)
                frame.write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
                reconstructed_V_k_1 = reconstructed_V_k # (j)

        except:
            print(colors.red(f'image_IPP_adaptive_codec.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise

    def T_codec(self, types, prefix, frame_number):
        frame.write(types, prefix + "types_", frame_number)

    def compute_br(self, prefix, frames_per_second, frame_shape, n_frames):
        kbps, bpp , n_bytes = image_IPP.compute_br(prefix, frames_per_second, frame_shape, n_frames)

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

codec = image_IPP_quantized_residue_codec()
def encode(video, n_frames, q_step):
    codec.encode(video, n_frames, q_step)

def compute_br(prefix, frames_per_second, frame_shape, n_frames):
    return codec.compute_br(prefix, frames_per_second, frame_shape, n_frames)
