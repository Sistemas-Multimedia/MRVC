''' MRVC/image_IPP.py '''

# Simple IPP block-based video compressor. Only P blocks are allowed
# in P-type frames. Input is RGB. No chroma subsampling.

import DWT
import LP
import numpy as np
import deadzone_quantizer as Q
import motion
import image_3 as frame_3
import image_1
import colored
import cv2
import os
import subprocess
import random
import config

if config.color == "YCoCg":
    import YCoCg as YUV

if config.color == "YCrCb":
    import YCrCb as YUV

if config.color == "RGB":
    import RGB as YUV

if config.spatial_codec == "DCT":
    import block_DCT

import logging
logger = logging.getLogger(__name__)
#logging.basicConfig(format="[%(filename)s:%(lineno)s %(levelname)s probando %(funcName)s()] %(message)s")
##logger.setLevel(logging.CRITICAL)
##logger.setLevel(logging.ERROR)
##logger.setLevel(logging.WARNING)
#logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

#self = sys.modules[__name__]
#print(self)

class image_IPP_codec():

    log2_block_side = 4
    block_x_side = 2**log2_block_side
    block_y_side = 2**log2_block_side
    N_components = 3
    
    def encode(self,
               video,    # Prefix of the original sequence of PNG images
               first_frame = 0,
               n_frames = 16, # Number of frames to process
               q_step = 1):  # Quantization step
        logger.info("Running ...")
        try:
            k = first_frame
            V_k = frame_3.read(video, k).astype(np.int16) - 128
            self.create_structures(V_k, image_IPP_codec.block_y_side, image_IPP_codec.block_x_side)
            W_k = YUV.from_RGB(V_k) # (a)
            W_k_1 = W_k # (b)
            E_k = W_k # (f)
            dequantized_E_k, QE_k = self.I_codec(E_k, f"{video}texture_", first_frame, q_step) # (g and h)
            reconstructed_W_k = dequantized_E_k # (i)
            if __debug__:
                frame_3.debug_write(self.clip(YUV.to_RGB(dequantized_E_k) + 128), f"{video}reconstructed_", k) # Decoder's output
            reconstructed_W_k_1 = reconstructed_W_k # (k)
            for k in range(first_frame + 1, first_frame + n_frames):
                V_k = frame_3.read(video, k).astype(np.int16) - 128
                W_k = YUV.from_RGB(V_k) # (a)
                averages = self.compute_averages(reconstructed_W_k, image_IPP_codec.block_y_side, image_IPP_codec.block_x_side)
                logger.debug(f"W_k {W_k[...,2].max()} {W_k[...,2].min()}")
                flow = motion.Farneback_ME(W_k[...,0], W_k_1[...,0], self.initial_flow) # (c)
                logger.debug(f"COMPUTED flow {flow.max()} {flow.min()}")
                W_k_1 = W_k # (b)
                reconstructed_flow = self.V_codec(flow, self.log2_block_side, f"{video}motion_", k) # (d and e)
                logger.debug(f"USED flow {reconstructed_flow.max()} {reconstructed_flow.min()}")
                prediction_W_k = motion.make_prediction(reconstructed_W_k_1, reconstructed_flow) # (j)
                if __debug__:
                    frame_3.debug_write(self.clip(YUV.to_RGB(prediction_W_k) + 128), f"{video}prediction_", k)
                E_k = W_k - prediction_W_k[:W_k.shape[0], :W_k.shape[1], :] # (f)
                if __debug__:
                    frame_3.debug_write(self.clip(YUV.to_RGB(E_k) + 128), f"{video}prediction_error_", k)
                dequantized_E_k, QE_k = self.E_codec4(E_k, f"{video}texture_", k, q_step * 2) # (g and h)
                if __debug__:
                    frame_3.debug_write(self.clip(YUV.to_RGB(dequantized_E_k) + 128), f"{video}dequantized_prediction_error_", k)
                reconstructed_W_k = dequantized_E_k + prediction_W_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1], :] # (i)
                reconstructed_W_k = self.decide_types(video, k, q_step, W_k, reconstructed_W_k, E_k, prediction_W_k, QE_k, image_IPP_codec.block_y_side, image_IPP_codec.block_x_side, averages)
                if __debug__:
                    frame_3.debug_write(self.clip(YUV.to_RGB(reconstructed_W_k) + 128), f"{video}reconstructed_", k) # Decoder's output
                reconstructed_W_k_1 = reconstructed_W_k # (k)
        except:
            print(colored.fore.RED + f'image_IPP.encode(video="{video}", first_frame={first_frame}, n_frames={n_frames}, q_step={q_step})')
            raise

    def create_structures(self, V_k, block_y_side, block_x_side):
        self.initial_flow = np.zeros((V_k.shape[0], V_k.shape[1], 2), dtype=np.float32)

    def compute_averages(self, V_k, block_y_side, block_x_side):
        pass

    def decide_types(self, video, k, q_step, V_k, reconstructed_V_k, E_k, prediction_V_k, QE_k, block_y_side, block_x_side, averages):
        return reconstructed_V_k

    def compute_br(self, prefix, frames_per_second, frame_shape, first_frame, n_frames):
        if config.spatial_codec == "MP4":
            return self.compute_br_MP4(prefix, frames_per_second, frame_shape, first_frame, n_frames)
        elif config.spatial_codec == "DCT":
            return self.compute_br_DCT(prefix, frames_per_second, frame_shape, first_frame, n_frames)

    def compute_br_DCT(self, prefix, frames_per_second, frame_shape, first_frame, n_frames):

        frame_height = frame_shape[0]
        frame_width = frame_shape[1]
        n_channels = frame_shape[2]
        sequence_time = n_frames/frames_per_second
        logger.info(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")

        # Texture.
        #texture_bytes = 0
        #for k in range(first_frame, first_frame + n_frames):
        #    _bytes = os.path.getsize(f"{prefix}texture_{k:03d}.png")
        #    texture_bytes += _bytes
        #    logger.debug(f"{prefix}texture_{k:03d}.png {_bytes} bytes")
        command = f"cat {prefix}texture_???.png | gzip -9 > /tmp/image_IPP_texture.gz"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        texture_bytes = os.path.getsize(f"/tmp/image_IPP_texture.gz")
        total_bytes = texture_bytes
        kbps = texture_bytes*8/sequence_time/1000
        bpp = texture_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        logger.info(f"texture: {texture_bytes} bytes, {kbps} KBPS, {bpp} BPP")

        # Motion. Y component.
        prev_comp = image_1.read(prefix + "motion_y_", first_frame + 1).astype(np.int16) - 128
        #prev_fn = f"{prefix}motion_y_001.png"
        #comp_length = os.path.getsize(prev_fn)
        for k in range(first_frame + 2, first_frame + n_frames):
            next_comp = image_1.read(prefix + "motion_y_", k).astype(np.int16) - 128 # Sobra astype
            #logger.debug(f"shapes {prev_comp.shape} {next_comp.shape}")
            #next_fn = f"{prefix}motion_y_{k:03d}.png"
            diff_comp = next_comp - prev_comp
            image_1.write((diff_comp.astype(np.int16) + 128).astype(np.uint8), prefix + "motion_y_diff_comp_", k)
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
        command = f"cat {prefix}motion_y_diff_comp_???.png | gzip -9 > /tmp/image_IPP_motion_y.gz"
        logger.debug(command)
        #os.system(command)
        subprocess.call(["bash", "-c", command])
        comp_length = os.path.getsize(f"/tmp/image_IPP_motion_y.gz")
        kbps = comp_length*8/sequence_time/1000
        bpp = comp_length*8/(frame_width*frame_height*n_channels*n_frames)
        logger.info(f"motion (Y direction): {comp_length} bytes, {kbps} KBPS, {bpp} BPP")
        total_bytes += comp_length

        # Motion. X component.
        prev_comp = image_1.read(prefix + "motion_x_", first_frame + 1).astype(np.int16) - 128
        #prev_fn = f"{prefix}motion_x_001.png"
        #comp_length = os.path.getsize(prev_fn)
        for k in range(first_frame + 2, first_frame + n_frames):
            next_comp = image_1.read(prefix + "motion_x_", k).astype(np.int16) - 128
            #next_fn = f"{prefix}motion_x_{k:03d}.png"
            diff_comp = next_comp - prev_comp
            image_1.write((diff_comp.astype(np.int16) + 128).astype(np.uint8), prefix + "motion_x_diff_comp_", k)
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
        command = f"cat {prefix}motion_x_diff_comp_???.png | gzip -9 > /tmp/image_IPP_motion_y.gz"
        logger.debug(command)
        #os.system(command)
        subprocess.call(["bash", "-c", command])
        comp_length = os.path.getsize(f"/tmp/image_IPP_motion_y.gz")    
        kbps = comp_length*8/sequence_time/1000
        bpp = comp_length*8/(frame_width*frame_height*n_channels*n_frames)
        logger.info(f"motion (X direction): {comp_length} bytes, {kbps} KBPS, {bpp} BPP")
        total_bytes += comp_length

        # Totals.
        kbps = total_bytes*8/sequence_time/1000
        bpp = total_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        #print(f"total: {kbps} KBPS, {bpp} BPP")

        return kbps, bpp, total_bytes

    def compute_br_MP4(self, prefix, frames_per_second, frame_shape, first_frame, n_frames):

        frame_height = frame_shape[0]
        frame_width = frame_shape[1]
        n_channels = frame_shape[2]
        sequence_time = n_frames/frames_per_second
        logger.info(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")

        # Texture.
        command = f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {prefix}texture_*.mp4; do echo \"file '$f'\"; done) -c copy /tmp/image_IPP_texture.mp4"
        #command = f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {prefix}texture_*.mp4; do echo \"file '$f'\"; done) -crf 0 /tmp/image_IPP_texture.mp4"
        #command = f"ffmpeg -loglevel fatal -y -i {prefix}texture_%03d.png -crf 0 /tmp/image_IPP_texture.mp4"
        logger.debug(command)
        #os.system(command)
        subprocess.call(["bash", "-c", command])
        texture_bytes = os.path.getsize("/tmp/image_IPP_texture.mp4")
        total_bytes = texture_bytes
        kbps = texture_bytes*8/sequence_time/1000
        bpp = texture_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        logger.info(f"texture: {texture_bytes} bytes, {kbps} KBPS, {bpp} BPP")

        # Motion. Y component.
        prev_comp = image_1.read(prefix + "motion_y_", 1).astype(np.int16) - 128
        #prev_fn = f"{prefix}motion_y_001.png"
        #comp_length = os.path.getsize(prev_fn)
        for k in range(first_frame + 2, first_frame + n_frames):
            next_comp = image_1.read(prefix + "motion_y_", k).astype(np.int16) + 128 # Sobra astype
            #next_fn = f"{prefix}motion_y_{k:03d}.png"
            diff_comp = next_comp - prev_comp
            image_1.write((diff_comp.astype(np.int16) + 128).astype(np.uint8), prefix + "motion_y_diff_comp_", k)
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
        command = f"cat {prefix}motion_y_diff_comp_???.png | gzip -9 > /tmp/image_IPP_motion_y.gz"
        logger.debug(command)
        #os.system(command)
        subprocess.call(["bash", "-c", command])
        comp_length = os.path.getsize(f"/tmp/image_IPP_motion_y.gz")
        kbps = comp_length*8/sequence_time/1000
        bpp = comp_length*8/(frame_width*frame_height*n_channels*n_frames)
        logger.info(f"motion (Y direction): {comp_length} bytes, {kbps} KBPS, {bpp} BPP")
        total_bytes += comp_length

        # Motion. X component.
        prev_comp = image_1.read(prefix + "motion_x_", 1).astype(np.int16) - 128
        prev_fn = f"{prefix}motion_x_001.png"
        #comp_length = os.path.getsize(prev_fn)
        for k in range(first_frame + 2, first_frame + n_frames):
            next_comp = image_1.read(prefix + "motion_x_", k).astype(np.int16) - 128
            #next_fn = f"{prefix}motion_x_{k:03d}.png"
            diff_comp = next_comp - prev_comp
            image_1.write((diff_comp.astype(np.int16) + 128).astype(np.uint8), prefix + "motion_x_diff_comp_", k)
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
        command = f"cat {prefix}motion_x_diff_comp_???.png | gzip -9 > /tmp/image_IPP_motion_x.gz"
        logger.debug(command)
        #os.system(command)
        subprocess.call(["bash", "-c", command])
        comp_length = os.path.getsize(f"/tmp/image_IPP_motion_x.gz")    
        kbps = comp_length*8/sequence_time/1000
        bpp = comp_length*8/(frame_width*frame_height*n_channels*n_frames)
        logger.info(f"motion (X direction): {comp_length} bytes, {kbps} KBPS, {bpp} BPP")
        total_bytes += comp_length

        # Totals.
        kbps = total_bytes*8/sequence_time/1000
        bpp = total_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        #print(f"total: {kbps} KBPS, {bpp} BPP")

        return kbps, bpp, total_bytes

    def I_codec(self, W_k, prefix, k, q_step):
        if config.spatial_codec == "H264":
            return self.I_codec_MP4(W_k, prefix, k, q_step)
        if config.spatial_codec == "DCT":
            return self.I_codec_DCT(W_k, prefix, k, q_step)

    def I_codec_DCT(self, W_k, prefix, k, Q_step):
        ''' Compress and decompress W_k using the NxN-DCT.'''
        coefs = block_DCT.analyze_image(W_k, self.block_y_side, self.block_x_side)
        Q_indexes_in_blocks = block_DCT.uniform_quantize(coefs, self.block_y_side, self.block_x_side, image_IPP_codec.N_components, Q_step)
        Q_coefs_in_blocks = block_DCT.uniform_dequantize(Q_indexes_in_blocks, self.block_y_side, self.block_x_side, image_IPP_codec.N_components, Q_step)
        Q_indexes_in_subbands = block_DCT.get_subbands(Q_indexes_in_blocks, self.block_y_side, self.block_x_side)
        _bytes = frame_3.write((Q_indexes_in_subbands + 128).astype(np.uint8), prefix, k)
        #_bytes = frame_3.write((Q_indexes_in_blocks + 128).astype(np.uint8), prefix, k)
        dQ_W_k = block_DCT.synthesize_image(Q_coefs_in_blocks, self.block_y_side, self.block_x_side)
        return dQ_W_k, Q_indexes_in_blocks

    def I_codec_MP4(self, W_k, prefix, k, q_step):
        to_write = YUV.to_RGB(W_k)
        to_write += 128
        to_write = to_write.astype(np.uint8)
        logger.debug(f"max={to_write.max()} min={to_write.min()} type={to_write.dtype}")
        frame_3.debug_write(to_write, prefix + "before_", k)
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264 -vf format=yuv420p -crf {q_step} {prefix}{k:03d}.mp4")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264 -vf format=yuv444p -crf {q_step} {prefix}{k:03d}.mp4"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        from_read = frame_3.read(prefix, k).astype(np.int16) - 128
        dq_W_k = YUV.from_RGB(from_read)
        return dq_W_k

    def I_codec2(E_k, prefix, k, q_step):
        #print("error", E_k.max(), E_k.min())
        #frame_3.write(clip(YUV.to_RGB(E_k)), prefix + "_to_mp4", k)
        frame_3.debug_write(YUV.to_RGB(E_k), prefix + "before_", k)
        command = f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} {prefix}{k:03d}.mp4"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        
        command = f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        
        dq_E_k = YUV.from_RGB(frame_3.read(prefix, k))
        #return dq_E_k.astype(np.float64)
        return dq_E_k

    def E_codec4(self, E_k, prefix, k, Q_step):
        if config.spatial_codec == "H264":
            if config.color == "YCrCb":
                return self.E_codec4_YCrCb_MP4(E_k, prefix, k, Q_step)
            elif config.color == "YCoCg":
                return self.E_codec4_YCoCg_MP4(E_k, prefix, k, Q_step)
        elif config.spatial_codec == "DCT":
            return self.E_codec4_DCT(E_k, prefix, k, Q_step)
            #return self.E_codec4_DCT(E_k, prefix, k, Q_step * 2000)

    def E_codec4_DCT(self, E_k, prefix, k, Q_step):
        logger.info(f"prefix={prefix} k={k} Q_step={Q_step}")
        return self.I_codec(E_k, prefix, k, Q_step)

    def E_codec4_YCoCg_MP4(self, E_k, prefix, k, q_step):
        offset = 128
        logger.debug(f"q_step {q_step}")
        logger.debug(f"error {E_k.max()} {E_k.min()} {E_k.dtype}")
        to_write = self.clip(YUV.to_RGB(E_k) + offset)
        logger.debug(f"max={to_write.max()} min={to_write.min()} type={to_write.dtype}")
        frame_3.debug_write(to_write, prefix + "before_", k)
        command = f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264 -vf format=yuv440p -crf {q_step} -flags -loop {prefix}{k:03d}.mp4"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        
        dq_E_k = (YUV.from_RGB(frame_3.read(prefix, k).astype(np.int16) - offset))
        logger.debug(f"deQ error YUV {dq_E_k.max()} {dq_E_k.min()} {dq_E_k.dtype}")    
        #dq_E_k = Q.dequantize(dq_E_k, 4)
        #return dq_E_k.astype(np.float64)
        return dq_E_k, None

    def E_codec4_YCrCb_MP4(self, E_k, prefix, k, q_step):
        offset = 0
        logger.debug(f"q_step {q_step}")
        logger.debug(f"error {E_k.max()} {E_k.min()} {E_k.dtype}")
        #frame_3.write(clip(YUV.to_RGB(E_k)), prefix + "_to_mp4", k)
        #frame_3.write(clip(YUV.to_RGB(E_k)+128), prefix + "_to_mp4_", k)
        #E_k = Q.quantize(E_k, 4)
        to_write = self.clip(YUV.to_RGB(E_k) + offset)
        logger.debug(f"max={to_write.max()} min={to_write.min()} type={to_write.dtype}")
        frame_3.debug_write(to_write, prefix + "before_", k)
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}.png -crf {q_step} {prefix}_{k:03d}.mp4")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} {prefix}{k:03d}.mp4")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264 -vf format=yuv420p -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264 -vf format=yuv440p -crf {q_step} -flags -loop {prefix}{k:03d}.mp4"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])

        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        
        dq_E_k = (YUV.from_RGB(frame_3.read(prefix, k).astype(np.int16) - offset))
        logger.debug(f"deQ error YUV {dq_E_k.max()} {dq_E_k.min()} {dq_E_k.dtype}")    
        #dq_E_k = Q.dequantize(dq_E_k, 4)
        #return dq_E_k.astype(np.float64)
        return dq_E_k, None

    def E_codec5(self, E_k, prefix, k, q_step):
        logger.debug(f"q_step {q_step}")
        logger.debug(f"error YUV {E_k.max()} {E_k.min()} {E_k.dtype}")
        #frame_3.write(np.clip(YUV.to_RGB(E_k)+256, 0, 512).astype(np.uint16), prefix + "before_", k)
        E_k = YUV.to_RGB(E_k)
        E_k += 256
        E_k *= 64
        E_k = np.array(E_k, dtype=np.uint16)
        logger.debug(f"error RGB {E_k.max()} {E_k.min()} {E_k.dtype}")    
        frame_3.debug_write(E_k, prefix + "before_", k)

        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}.png -crf {q_step} {prefix}_{k:03d}.mp4")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -crf {q_step} {prefix}{k:03d}.mp4")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264rgb -vf format=yuv444p -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}before_{k:03d}.png -c:v libx264rgb -vf format=yuv444p -crf {q_step} -flags -loop {prefix}{k:03d}.mp4"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        #os.system(f"ffmpeg -y -i {prefix}before_{k:03d}.png -crf {q_step} -flags -loop {prefix}{k:03d}.mp4")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}{k:03d}.mp4 {prefix}{k:03d}.png"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        
        #dq_E_k = (YUV.from_RGB(frame_3.read(prefix, k).astype(np.int16) - 256))
        dq_E_k = frame_3.read(prefix, k)
        logger.debug(f"deQ error RGB {dq_E_k.max()} {dq_E_k.min()} {dq_E_k.dtype}")    
        dq_E_k //= 64
        dq_E_k -= 256
        dq_E_k = np.array(dq_E_k, dtype=np.int16)
        dq_E_k = YUV.from_RGB(dq_E_k)

        logger.debug(f"deQ error YUV {dq_E_k.max()} {dq_E_k.min()} {dq_E_k.dtype}")
        #dq_E_k = Q.dequantize(dq_E_k, 4)
        #return dq_E_k.astype(np.float64)
        return dq_E_k

    def V_codec(self, motion, n_levels, prefix, frame_number):
        #return motion
        pyramid = LP.analyze(motion, n_levels)
        image_1.debug_write((pyramid[0][...,0].astype(np.int16) + 128).astype(np.uint8), prefix + "x_", frame_number)
        image_1.debug_write((pyramid[0][...,1].astype(np.int16) + 128).astype(np.uint8), prefix + "y_", frame_number)
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
        return (frame_3.normalize(x)*255).astype(np.uint8)

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
        logger.debug(f"error {E_k.max()} {E_k.min()}")
        image_3.debug_write(YUV.to_RGB(E_k), prefix + "_to_mp4", k)
        #frame_3.write(YUV.to_RGB(E_k), prefix + "_to_mp4", k)
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}.png -crf 1 {prefix}_{k:03d}.mp4")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}_to_mp4_{k:03d}.png -crf 1 {prefix}_{k:03d}.mp4"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        
        #os.system(f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        
        dq_E_k = YUV.from_RGB(image_3.read(prefix + "_from_mp4", k))
        #dq_E_k = (YUV.from_RGB(frame_3.read(prefix + "_from_mp4", k)))
        return dq_E_k.astype(np.float64)

    def _V_codec(motion, n_levels, prefix, frame_number):
        pyramid = np.rint(motion).astype(np.int16)
        frame_3.write(pyramid[:,:,0], prefix+"_x_", frame_number)
        frame_3.write(pyramid[:,:,1], prefix+"_y_", frame_number)
        return pyramid

    def compute_br2(prefix, frames_per_second, frame_shape, first_frame, n_frames):
        #print("*"*80, prefix)
        #os.system(f"ffmpeg -y -i {prefix}_from_mp4_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_texture.mp4")
        #os.system(f"ffmpeg -f concat -safe 0 -i <(for f in {prefix}_*.mp4; do echo \"file '$PWD/$f'\"; done) -c copy /tmp/image_IPP_texture.mp4")
        command = f"ffmpeg -loglevel fatal -y -f concat -safe 0 -i <(for f in {prefix}texture_*.mp4; do echo \"file '$f'\"; done) -c copy /tmp/image_IPP_texture.mp4"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        #print(f"ffmpeg -loglevel fatal -y -i {prefix}motion_y_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_motion_y.mp4")
        command = f"ffmpeg -loglevel fatal -y -i {prefix}motion_y_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_motion_y.mp4"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])
        command = f"ffmpeg -loglevel fatal -y -i {prefix}motion_x_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_motion_x.mp4"
        logger.debug(command)
        subprocess.call(["bash", "-c", command])

        frame_height = frame_shape[0]
        frame_width = frame_shape[1]
        n_channels = frame_shape[2]
        sequence_time = n_frames/frames_per_second
        logger.info(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")

        texture_bytes = os.path.getsize("/tmp/image_IPP_texture.mp4")
        total_bytes = texture_bytes
        kbps = texture_bytes*8/sequence_time/1000
        bpp = texture_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        logger.info(f"texture: {texture_bytes} bytes, {kbps} KBPS, {bpp} BPP")

        motion_y_bytes = os.path.getsize("/tmp/image_IPP_motion_y.mp4")
        total_bytes += motion_y_bytes
        kbps = motion_y_bytes*8/sequence_time/1000
        logger.info(f"motion (Y direction): {motion_y_bytes} bytes, {kbps} KBPS")

        motion_x_bytes = os.path.getsize("/tmp/image_IPP_motion_x.mp4")
        total_bytes += motion_x_bytes
        kbps = motion_x_bytes*8/sequence_time/1000
        logger.info(f"motion (X direction): {motion_x_bytes} bytes, {kbps} KBPS")

        total_bytes += motion_x_bytes
        kbps = total_bytes*8/sequence_time/1000
        bpp = total_bytes*8/(frame_width*frame_height*n_channels*n_frames)
        #print(f"total: {kbps} KBPS, {bpp} BPP")

        return kbps, bpp

codec = image_IPP_codec()
def encode(video, first_frame, n_frames, q_step):
    codec.encode(video, first_frame, n_frames, q_step)

def compute_br(prefix, frames_per_second, frame_shape, first_frame, n_frames):
    return codec.compute_br(prefix, frames_per_second, frame_shape, first_frame, n_frames)

# https://stackoverflow.com/questions/34123272/ffmpeg-transmux-mpegts-to-mp4-gives-error-muxer-does-not-support-non-seekable: ffmpeg -blocksize 1 -i /tmp/original_000.png -blocksize 1 -flush_packets 1 -movflags frag_keyframe+empty_moov -f mp4 - | ffmpeg -blocksize 1 -i - -blocksize 1 -flush_packets 1 /tmp/decoded_%3d.png

# https://video.stackexchange.com/questions/16958/ffmpeg-encode-in-all-i-mode-h264-and-h265-streams: fmpeg -i input -c:v libx264 -intra output / ffmpeg -i input -c:v libx265 -x265-params frame-threads=4:keyint=1:ref=1:no-open-gop=1:weightp=0:weightb=0:cutree=0:rc-lookahead=0:bframes=0:scenecut=0:b-adapt=0:repeat-headers=1 output

