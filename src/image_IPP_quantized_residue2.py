''' MRVC/image_IPP_quantized_residue.py '''

# The residue is quantized depending on the distortion generated in the previous frame.
#
# Delta = 8 - int(log_2(average_absolute_error_of_the_block))
# average_absolute_error_of_the_block = Sum |pixels_difference| / number_of_pixels
#

import math
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
#np.set_printoptions(linewidth=2000)
import config
if config.color == "YCoCg":
    import YCoCg as YUV

if config.color == "YCrCb":
    import YCrCb as YUV

if config.color == "RGB":
    import RGB as YUV

class image_IPP_quantized_residue_codec(image_IPP.image_IPP_codec):

    def encode(self, video, first_frame, n_frames, q_step):
        try:
            k = first_frame
            W_k = frame.read(video, k).astype(np.int16)
            initial_flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)
            blocks_in_y = int(W_k.shape[0]/self.block_y_side)
            blocks_in_x = int(W_k.shape[1]/self.block_x_side)
            V_k = YUV.from_RGB(W_k) # (a)
            V_k_1 = V_k # (b)
            E_k = V_k # (f)
            dequantized_E_k = self.I_codec(V_k, f"{video}texture_", 0, 25)#q_step) # (g and h)
            reconstructed_V_k = dequantized_E_k # (i)
            frame.write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output

            # Quantization step of each block for the next frame
            block_delta = np.array(shape=(blocks_in_y, blocks_in_x), dtype=np.float32)
            for y in range(blocks_in_y):
                for x in range(blocks_in_x):
                    block_differences =
                    abs(V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                            x*self.block_x_side:(x+1)*self.block_x_side][..., 0] -
                    reconstructed_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                      x*self.block_x_side:(x+1)*self.block_x_side][..., 0])
                    block_distortion = np.sum(block_differences)
                    block_delta[y,x] = 8 - int(math.log(block_distortion)/math.log(2.0))
            
            reconstructed_V_k_1 = reconstructed_V_k # (j)
            for k in range(first_frame + 1, first_frame + n_frames):
                W_k = frame.read(video, k).astype(np.int16)
                V_k = YUV.from_RGB(W_k) # (a)
                flow = motion.estimate(V_k[...,0], V_k_1[...,0], initial_flow) # (c)
                V_k_1 = V_k # (b)
                reconstructed_flow = self.V_codec(flow, self.log2_block_side, f"{video}motion_", k) # (d and e)
                prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow) # (j)

                # Compute the current slopes
                for y in range(blocks_in_y):
                    for x in range(blocks_in_x):
                        predicted_block = V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                              x*self.block_x_side:(x+1)*self.block_x_side][..., 0]
                        prediction_block = prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                          x*self.block_x_side:(x+1)*self.block_x_side][..., 0]
                        block_RD_slope[y][x] = compute_block_slope(predicted_block, prediction_block, 32)#q_step)

                # Find the median slope
                #min_RD_slope = np.unravel_index(np.argmin(block_RD_slope, axis=None), block_RD_slope.shape)

                #for y in range(blocks_in_y):
                #    print("\n=======antes=====", end=' ')
                #    for x in range(blocks_in_x):
                #        print(block_RD_slope[y][x], end=' ')
                median_RD_slope = np.median(block_RD_slope)
                print("========== median_RD_slope =", median_RD_slope)

                # Decrease the slope of those blocks with a slope higher than the smaller one(s)
                for y in range(blocks_in_y):
                    for x in range(blocks_in_x):
                        while block_RD_slope[y][x] > median_RD_slope:
                            next_Q_step = block_Q_step[y][x] - 1
                            if next_Q_step <= 0:
                                break
                            predicted_block = V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                  x*self.block_x_side:(x+1)*self.block_x_side][..., 0]
                            prediction_block = prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                              x*self.block_x_side:(x+1)*self.block_x_side][..., 0]
                            old_slope = block_RD_slope[y][x]
                            block_RD_slope[y][x] = compute_block_slope(predicted_block, prediction_block, next_Q_step)
                            if old_slope == block_RD_slope[y][x]:
                                break
                            block_Q_step[y][x] = next_Q_step
                            #print("%%%%%", y, x, block_RD_slope[y][x], median_RD_slope, block_Q_step[y][x])
                        while block_RD_slope[y][x] < median_RD_slope:
                            next_Q_step = block_Q_step[y][x] + 1
                            if next_Q_step >= 64:
                                break
                            predicted_block = V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                  x*self.block_x_side:(x+1)*self.block_x_side][..., 0]
                            prediction_block = prediction_V_k[y*self.block_y_side:(y+1)*self.block_y_side,
                                                              x*self.block_x_side:(x+1)*self.block_x_side][..., 0]
                            old_slope = block_RD_slope[y][x]
                            block_RD_slope[y][x] = compute_block_slope(predicted_block, prediction_block, next_Q_step)
                            if old_slope == block_RD_slope[y][x]:
                                break
                            block_Q_step[y][x] = next_Q_step
                        #block_Q_step[y][x] = math.log(block_Q_step[y][x])+1
                        #if block_Q_step[y][x] > 1:
                        #    block_Q_step[y][x] = 64
                            #print("%%%%%", y, x, block_RD_slope[y][x], median_RD_slope, block_Q_step[y][x])
                #for y in range(blocks_in_y):
                #    print("\n=======despues=====", end=' ')
                #    for x in range(blocks_in_x):
                #        print(int(block_RD_slope[y][x]*100), end=' ')

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
                #print("ooooooooooooooo", dequantized_E_k.dtype)
                dequantized_E_k = self.E_codec4(dequantized_E_k, f"{video}texture_", k, q_step) # (g and h)

                frame.debug_write(self.clip(YUV.to_RGB(dequantized_E_k) + 128), f"{video}dequantized_prediction_error_", k)
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1], :] # (i)
                frame.write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
                reconstructed_V_k_1 = reconstructed_V_k # (j)

        except:
            print(colors.red(f'image_IPP_adaptive_codec.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise

    def T_codec(self, types, prefix, frame_number):
        for y in range(types.shape[0]):
            for x in range(types.shape[1]):
                debug.print(types[y][x], end=' ')
            print()
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
def encode(video, first_frame, n_frames, q_step):
    codec.encode(video, first_frame, n_frames, q_step)

def compute_br(prefix, frames_per_second, frame_shape, first_frame, n_frames):
    return codec.compute_br(prefix, frames_per_second, frame_shape, first_frame, n_frames)
