''' MRVC/image_IPP.py '''

# Simple IPP block-based video compressor. Prediction error blocks are
# quantized in the DCT domain to have the same slope in the RD curve,
# where the rate is estimated with the entropy of the block (after
# quantization in the DCT domain) and the distortion is measured
# between the original frame and the reconstructed one in the image
# domain. Quantizatized residues are entropy encoded as a single PNG
# image.

# To work with the same RD slope, all the blocks are transformed and
# quantized using the master q_step. Then, the median slope is used as
# reference for the rest of blocks. Thus if a block has a slope
# smaller than the median slope, a large quantization step is used
# until this condition is false, and viceversa.

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
import debug
#import sys
import config

if config.color == "YCoCg":
    import YCoCg as YUV

if config.color == "YCrCb":
    import YCrCb as YUV

if config.color == "RGB":
    import RGB as YUV

class image_IPP_codec():

    log2_block_side = 4
    block_x_side = 2**log2_block_side
    block_y_side = 2**log2_block_side

    def encode(self,
               video,    # Prefix of the original sequence of PNG images 
               n_frames, # Number of frames to process
               q_step):  # Master quantization step
        try:
            k = 0
            W_k = frame.read(video, k).astype(np.int16)
            self.initial_flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)
            V_k = YUV.from_RGB(W_k) # (a)
            V_k_1 = V_k # (b)
            E_k = V_k # (f)
            #frame.debug_write(YUV.to_RGB(E_k), f"{video}_prediction_error", k)
            #dequantized_E_k = E_codec(E_k, N_LEVELS, q_step, codestream, 0) # (g and h)
            dequantized_E_k = self.I_codec(V_k, f"{video}texture_", 0, q_step) # (g and h)
            reconstructed_V_k = dequantized_E_k # (i)
            frame.debug_write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (j)
            for k in range(1, n_frames):
                W_k = frame.read(video, k).astype(np.int16)
                V_k = YUV.from_RGB(W_k) # (a)
                averages = self.compute_averages(V_k, image_IPP_codec.block_y_side, image_IPP_codec.block_x_side)
                debug.print("V_k", V_k[...,2].max(), V_k[...,2].min())
                #flow = motion.estimate(V_k[...,0], V_k_1[...,0], flow) # (c)
                #initial_flow = np.zeros((V_k.shape[0], V_k.shape[1], 2), dtype=np.float32)
                flow = motion.estimate(V_k[...,0], V_k_1[...,0], self.initial_flow) # (c)
                #flow = motion.full_search_motion_estimation(V_k[...,0], V_k_1[...,0])
                #flow = np.rint(flow)
                #flow = np.random.randint(-1, 1, flow.shape).astype(np.float32)
                #print("flow.dtype=", flow.dtype, "flow.max()=", flow.max(), "flow.min()=", flow.min())
                debug.print("COMPUTED flow", flow.max(), flow.min())
                V_k_1 = V_k # (b)
                reconstructed_flow = self.V_codec(flow, self.log2_block_side, f"{video}motion_", k) # (d and e)
                debug.print("USED flow", reconstructed_flow.max(), reconstructed_flow.min())
                #frame.debug_write(motion.colorize(flow), f"{codestream}flow", k)
                #frame.debug_write(motion.colorize(reconstructed_flow.astype(np.float32)), f"{codestream}reconstructed_flow", k)
                #prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow).astype(np.int16) # (j)
                prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow) # (j)
                frame.debug_write(self.clip(YUV.to_RGB(prediction_V_k)), f"{video}prediction_", k)
                E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
                frame.debug_write(self.clip(YUV.to_RGB(E_k)+128), f"{video}prediction_error_", k)
                #dequantized_E_k = E_codec(E_k, 5, q_step, codestream, k) # (g and h)
                dequantized_E_k = self.E_codec4(E_k, f"{video}texture_", k, q_step) # (g and h)
                #print(dequantized_E_k.dtype, dequantized_E_k.shape)
                #quantized_E_k = Q.quantize(E_k, step=q_step) # (e)
                #dequantized_E_k = Q.dequantize(quantized_E_k, step=q_step) # (f)
                frame.debug_write(self.clip(YUV.to_RGB(dequantized_E_k) + 128), f"{video}dequantized_prediction_error_", k)
                reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1], :] # (i)
                #print(reconstructed_V_k.dtype, reconstructed_V_k.shape)
                #L.write(reconstructed_V_k, video + "reconstructed", k)
                reconstructed_V_k = self.decide_types(video, k, q_step, V_k, reconstructed_V_k, E_k, prediction_V_k, image_IPP_codec.block_y_side, image_IPP_codec.block_x_side, averages)
                frame.debug_write(self.clip(YUV.to_RGB(reconstructed_V_k)), f"{video}reconstructed_", k) # Decoder's output
                reconstructed_V_k_1 = reconstructed_V_k # (j)
        except:
            print(colors.red(f'image_IPP.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
            raise
        
    def decide_types(self, video, k, q_step, V_k, reconstructed_V_k, E_k, prediction_V_k, block_y_side, block_x_side, averages):
        return reconstructed_V_k

    def compute_br(self, prefix, frames_per_second, frame_shape, n_frames):

        frame_height = frame_shape[0]
        frame_width = frame_shape[1]
        n_channels = frame_shape[2]
        sequence_time = n_frames/frames_per_second
        print(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")

        # Texture.
        command = f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {prefix}texture_*.mp4; do echo \"file '$f'\"; done) -c copy /tmp/image_IPP_texture.mp4"
        #command = f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {prefix}texture_*.mp4; do echo \"file '$f'\"; done) -crf 0 /tmp/image_IPP_texture.mp4"
        #command = f"ffmpeg -loglevel fatal -y -i {prefix}texture_%03d.png -crf 0 /tmp/image_IPP_texture.mp4"
        print(command)
        os.system(command)
        texture_bytes = os.path.getsize("/tmp/image_IPP_texture.mp4")
        total_bytes = texture_bytes
        kbps = texture_bytes*8/sequence_time/1000
        bpp = texture_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        print(f"texture: {texture_bytes} bytes, {kbps} KBPS, {bpp} BPP")

        # Motion. Y component.
        prev_comp = L.read(prefix + "motion_y_", 1).astype(np.int16) # Sobra astype
        #prev_fn = f"{prefix}motion_y_001.png"
        #comp_length = os.path.getsize(prev_fn)
        for k in range(2, n_frames):
            next_comp = L.read(prefix + "motion_y_", k).astype(np.int16) # Sobra astype
            #next_fn = f"{prefix}motion_y_{k:03d}.png"
            diff_comp = next_comp - prev_comp
            L.write(diff_comp, prefix + "motion_y_diff_comp_", k)
            #comp_length += os.path.getsize(f"{prefix}motion_y_diff_comp_{k:03d}.png")
            '''
            # Count the number of common bytes starting and the beginning.
            counter = -2 # 2 bytes for representing the header size.
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
                    #print(".", end='')
                    counter += 1
            comp_length -= counter
            #print("counter =", counter)
            prev_comp = next_comp
            '''
        command = f"cat {prefix}motion_y_diff_comp_???LL.png | gzip -9 > /tmp/image_IPP_motion_y.gz"
        debug.print(command)
        os.system(command)
        comp_length = os.path.getsize(f"/tmp/image_IPP_motion_y.gz")
        kbps = comp_length*8/sequence_time/1000
        bpp = comp_length*8/(frame_width*frame_height*n_channels*n_frames)
        print(f"motion (Y direction): {comp_length} bytes, {kbps} KBPS, {bpp} BPP")
        total_bytes += comp_length

        # Motion. X component.
        prev_comp = L.read(prefix + "motion_x_", 1).astype(np.int16) # Sobra astype
        prev_fn = f"{prefix}motion_x_001.png"
        #comp_length = os.path.getsize(prev_fn)
        for k in range(2, n_frames):
            next_comp = L.read(prefix + "motion_x_", k).astype(np.int16) # Sobra astype
            #next_fn = f"{prefix}motion_x_{k:03d}.png"
            diff_comp = next_comp - prev_comp
            L.write(diff_comp, prefix + "motion_x_diff_comp_", k)
            #comp_length += os.path.getsize(f"{prefix}motion_x_diff_comp_{k:03d}.png")
            '''
            # Count the number of common bytes starting and the beginning.
            counter = -2
            with open(prev_fn, 'rb') as prev_f, open(next_fn, 'rb') as next_f:
                while True:
                    prev_byte = prev_f.read(1)
                    next_byte = next_f.read(1)
                    #print(prev_byte, next_byte)
                    if prev_byte != next_byte:
                        break
                    if prev_byte == b'':
                        break
                    if next_byte == b'':
                        break
                    counter += 1
            comp_length -= counter
            print("counter =", counter)
            prev_comp = next_comp
            '''
        command = f"cat {prefix}motion_x_diff_comp_???LL.png | gzip -9 > /tmp/image_IPP_motion_y.gz"
        debug.print(command)
        os.system(command)
        comp_length = os.path.getsize(f"/tmp/image_IPP_motion_y.gz")    
        kbps = comp_length*8/sequence_time/1000
        bpp = comp_length*8/(frame_width*frame_height*n_channels*n_frames)
        print(f"motion (X direction): {comp_length} bytes, {kbps} KBPS, {bpp} BPP")
        total_bytes += comp_length

        # Totals.
        kbps = total_bytes*8/sequence_time/1000
        bpp = total_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        #print(f"total: {kbps} KBPS, {bpp} BPP")

        return kbps, bpp, total_bytes

    def I_codec(self, V_k, prefix, k, q_step, blocks_in_y, blocks_in_x):
        '''Encode a I-frame. Blocks are DCT-ed and quantized using <q_step>. Because the DCT is orthogonal, we can compute the distortion of the dequantized block directly in the DCT domain. However, because the blocks need to be detransformed in order to generate the reconstructed frame, the distortion is computed in the image domain. The rate is the entropy of the quantized block in the DCT domain.'''
        block_slopes = np.array(shape=(blocks_in_y, blocks_in_x), dtype=np.float32)
        block_Q_step = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=32, dtype=np.uint8)

        # Compute the initial slopes
        for y in range(blocks_in_y):
            for x in range(blocks_in_x):
                block = V_k[y*block_y_side:(y+1)*block_y_side,
                            x*block_x_side:(x+1)*block_x_side][..., 0]
                DCT_block = dct(block, norm='ortho')
                quantized_DCT_block = Q.quantize(DCT_block, q_step)
                dequantized_DCT_block = Q.dequantize(quantized_DCT_block, q_step)
                dequantized_block = idct(dequantized_DCT_block, norm='ortho').astype(np.int16)
                RD_point_for_Q_step_one = (information.entropy(DCT_block.flatten().astype(np.int16)), 0)
                current_RD_point = (information.entropy(quantized_DCT_block.flatten()), distortion.MSE(block, dequantized_block))
                block_slopes[y,x] = current_RD_point[1] / (RD_point_for_Q_step_one[0] - current_RD_point[0])

        # Determine the median slope
        median_slope = np.median(block_slopes)

        # Move the quantization steps of the slopes with higher or
        # slower median_slope
        for y in range(blocks_in_y):
            for x in range(blocks_in_x):
                while block_slopes[y,x] > median_slope:
                    next_Q_step = block_Q_steps[y,x] - 1
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


    def E_codec4(self, E_k, prefix, k, q_step):
        if config.color == "YCrCb":
            return self.E_codec_4_YCrCb(E_k, prefix, k, q_step)
        elif config.color == "YCoCg":
            return self.E_codec_4_YCoCg(E_k, prefix, k, q_step)

    def E_codec_4_YCoCg(self, E_k, prefix, k, q_step):
        offset = 128
        debug.print("image_IPP.E_codec: q_step", q_step)
        debug.print("image_IPP.E_codec: error", E_k.max(), E_k.min(), E_k.dtype)
        #frame.write(clip(YUV.to_RGB(E_k)), prefix + "_to_mp4", k)
        #frame.write(clip(YUV.to_RGB(E_k)+128), prefix + "_to_mp4_", k)
        #E_k = Q.quantize(E_k, 4)
        to_write = self.clip(YUV.to_RGB(E_k) + offset)
        debug.print(f"image_IPP.E_codec: max={to_write.max()} min={to_write.min()} type={to_write.dtype}")
        frame.write(to_write, prefix + "before_", k)
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}.png -crf {q_step} {prefix}_{k:03d}.mp4")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} {prefix}{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264 -vf format=yuv420p -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")

        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        dq_E_k = (YUV.from_RGB(frame.read(prefix, k).astype(np.int16) - offset))
        debug.print("image_IPP.E_codec: deQ error YUV", dq_E_k.max(), dq_E_k.min(), dq_E_k.dtype)    
        #dq_E_k = Q.dequantize(dq_E_k, 4)
        #return dq_E_k.astype(np.float64)
        return dq_E_k

    def E_codec_4_YCrCb(self, E_k, prefix, k, q_step):
        offset = 0
        debug.print("image_IPP.E_codec: q_step", q_step)
        debug.print("image_IPP.E_codec: error", E_k.max(), E_k.min(), E_k.dtype)
        #frame.write(clip(YUV.to_RGB(E_k)), prefix + "_to_mp4", k)
        #frame.write(clip(YUV.to_RGB(E_k)+128), prefix + "_to_mp4_", k)
        #E_k = Q.quantize(E_k, 4)
        to_write = self.clip(YUV.to_RGB(E_k) + offset)
        debug.print(f"image_IPP.E_codec: max={to_write.max()} min={to_write.min()} type={to_write.dtype}")
        frame.write(to_write, prefix + "before_", k)
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}.png -crf {q_step} {prefix}_{k:03d}.mp4")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} {prefix}{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264 -vf format=yuv420p -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")

        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        dq_E_k = (YUV.from_RGB(frame.read(prefix, k).astype(np.int16) - offset))
        debug.print("image_IPP.E_codec: deQ error YUV", dq_E_k.max(), dq_E_k.min(), dq_E_k.dtype)    
        #dq_E_k = Q.dequantize(dq_E_k, 4)
        #return dq_E_k.astype(np.float64)
        return dq_E_k

    def E_codec5(self, E_k, prefix, k, q_step):
        debug.print("image_IPP.E_codec: q_step", q_step)
        debug.print("image_IPP.E_codec: error YUV", E_k.max(), E_k.min(), E_k.dtype)
        #frame.write(np.clip(YUV.to_RGB(E_k)+256, 0, 512).astype(np.uint16), prefix + "before_", k)
        E_k = YUV.to_RGB(E_k)
        E_k += 256
        E_k *= 64
        E_k = np.array(E_k, dtype=np.uint16)
        debug.print("image_IPP.E_codec: error RGB", E_k.max(), E_k.min(), E_k.dtype)    
        frame.write(E_k, prefix + "before_", k)

        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}.png -crf {q_step} {prefix}_{k:03d}.mp4")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} {prefix}{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264rgb -vf format=yuv444p -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
        #os.system(f"ffmpeg -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        #dq_E_k = (YUV.from_RGB(frame.read(prefix, k).astype(np.int16) - 256))
        dq_E_k = frame.read(prefix, k)
        debug.print("image_IPP.E_codec: deQ error RGB", dq_E_k.max(), dq_E_k.min(), dq_E_k.dtype)    
        dq_E_k //= 64
        dq_E_k -= 256
        dq_E_k = np.array(dq_E_k, dtype=np.int16)
        dq_E_k = YUV.from_RGB(dq_E_k)

        debug.print("image_IPP.E_codec: deQ error YUV", dq_E_k.max(), dq_E_k.min(), dq_E_k.dtype)
        #dq_E_k = Q.dequantize(dq_E_k, 4)
        #return dq_E_k.astype(np.float64)
        return dq_E_k

    def V_codec(self, motion, n_levels, prefix, frame_number):
        #print(prefix+"_y")
        pyramid = LP.analyze(motion, n_levels)
        #pyramid[0][:,:,:] = 0
        L.write(pyramid[0][...,0], prefix + "y_", frame_number)
        L.write(pyramid[0][...,1], prefix + "x_", frame_number)
        for resolution in pyramid[1:]:
            resolution[...] = 0
        reconstructed_motion = LP.synthesize(pyramid, n_levels)
        #print(motion-reconstructed_motion[:motion.shape[0], :motion.shape[1], :])
        #return np.rint(reconstructed_motion).astype(np.float32)
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

    def clip(self, x):
        return(np.clip(x, 0 ,255).astype(np.uint8))

    def norm(x):
        return (frame.normalize(x)*255).astype(np.uint8)

    def I_codec2(E_k, prefix, k, q_step):
        #print("error", E_k.max(), E_k.min())
        #frame.write(clip(YUV.to_RGB(E_k)), prefix + "_to_mp4", k)
        frame.write(YUV.to_RGB(E_k), prefix + "before_", k)
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} {prefix}{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        dq_E_k = (YUV.from_RGB(frame.read(prefix, k)))
        #return dq_E_k.astype(np.float64)
        return dq_E_k

    # Versión basada en DWT+Q
    def __E_codec(E_k, n_levels, q_step, prefix, k):
        decom = DWT.analyze(E_k, n_levels)
        #print(decom[0])
        LL = decom[0]
        decom[0] = Q.quantize(LL, q_step)
        for resolution in decom[1:]:
            resolution = list(resolution)
            LH = resolution[0]
            resolution[0][:] = Q.quantize(LH, q_step)
            HL = resolution[1]
            resolution[1][:] = Q.quantize(HL, q_step)
            HH = resolution[2]
            resolution[2][:] = Q.quantize(HH, q_step)
            resolution = tuple(resolution)
        DWT.write(decom, prefix, k, n_levels)
        LL = decom[0]
        #print(LL)
        decom[0] = Q.dequantize(LL, q_step)
        #print(decom[0])
        for resolution in decom[1:]:
            resolution = list(resolution)
            LH = resolution[0]
            resolution[0][:] = Q.dequantize(LH, q_step)
            HL = resolution[1]
            resolution[1][:] = Q.dequantize(HL, q_step)
            HH = resolution[2]
            resolution[2][:] = Q.dequantize(HH, q_step)
            resolution = tuple(resolution)
        #print("->", decom[1][0])
        dq_E_k = DWT.synthesize(decom, n_levels)
        return dq_E_k
        #return E_k-dq_E_k
        #return E_k

    '''
    def E_codec(E_k, prefix, k, q_step):
        assert q_step > 0
        decom = DWT.analyze(E_k, N_LEVELS)
        #print(decom[0])
        LL = decom[0]
        decom[0] = Q.quantize(LL, q_step)
        for resolution in decom[1:]:
            resolution = list(resolution)
            LH = resolution[0]
            resolution[0][:] = Q.quantize(LH, q_step)
            HL = resolution[1]
            resolution[1][:] = Q.quantize(HL, q_step)
            HH = resolution[2]
            resolution[2][:] = Q.quantize(HH, q_step)
            resolution = tuple(resolution)
        DWT.write(decom, prefix, k, N_LEVELS)
        LL = decom[0]
        #print(LL)
        decom[0] = Q.dequantize(LL, q_step)
        #print(decom[0])
        for resolution in decom[1:]:
            resolution = list(resolution)
            LH = resolution[0]
            resolution[0][:] = Q.dequantize(LH, q_step)
            HL = resolution[1]
            resolution[1][:] = Q.dequantize(HL, q_step)
            HH = resolution[2]
            resolution[2][:] = Q.dequantize(HH, q_step)
            resolution = tuple(resolution)
        #print("->", decom[1][0])
        dq_E_k = DWT.synthesize(decom, N_LEVELS)
        return dq_E_k
        #return E_k-dq_E_k
        #return E_k
    '''

    def E_codec2(E_k, prefix, k):
        print("error", E_k.max(), E_k.min())
        L.write(YUV.to_RGB(E_k), prefix + "_to_mp4", k)
        #frame.write(YUV.to_RGB(E_k), prefix + "_to_mp4", k)
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}_LL.png -crf 1 {prefix}_{k:03d}.mp4")
        os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}_LL.png")
        dq_E_k = YUV.from_RGB(L.read(prefix + "_from_mp4", k))
        #dq_E_k = (YUV.from_RGB(frame.read(prefix + "_from_mp4", k)))
        return dq_E_k.astype(np.float64)

    def _V_codec(motion, n_levels, prefix, frame_number):
        pyramid = np.rint(motion).astype(np.int16)
        frame.write(pyramid[:,:,0], prefix+"_y_", frame_number)
        frame.write(pyramid[:,:,1], prefix+"_x_", frame_number)
        return pyramid

    def compute_br2(prefix, frames_per_second, frame_shape, n_frames):
        #print("*"*80, prefix)
        #os.system(f"ffmpeg -y -i {prefix}_from_mp4_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_texture.mp4")
        #os.system(f"ffmpeg -f concat -safe 0 -i <(for f in {prefix}_*.mp4; do echo \"file '$PWD/$f'\"; done) -c copy /tmp/image_IPP_texture.mp4")
        command = f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {prefix}texture_*.mp4; do echo \"file '$f'\"; done) -c copy /tmp/image_IPP_texture.mp4"
        print(command)
        os.system(command)
        #print(f"ffmpeg -loglevel fatal -y -i {prefix}motion_y_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_motion_y.mp4")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}motion_y_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_motion_y.mp4"
        print(command)
        os.system(command)
        command = f"ffmpeg -loglevel fatal -y -i {prefix}motion_x_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_motion_x.mp4"
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

        total_bytes += motion_x_bytes
        kbps = total_bytes*8/sequence_time/1000
        bpp = total_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        #print(f"total: {kbps} KBPS, {bpp} BPP")

        return kbps, bpp

codec = image_IPP_codec()
def encode(video, n_frames, q_step):
    codec.encode(video, n_frames, q_step)

def compute_br(prefix, frames_per_second, frame_shape, n_frames):
    return codec.compute_br(prefix, frames_per_second, frame_shape, n_frames)
