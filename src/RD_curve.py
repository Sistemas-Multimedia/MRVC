''' MRVC/image_IPP_RD.py '''

# Generate a RD curve.

import config
import distortion
import frame

# --> Select below the codec. <--
#import image_interpolated_IPP as codec
#import image_IPP as codec
#import image_IPP_adaptive as codec
#import image_IPP_quantized_prediction as codec
import image_IPP_quantized_residue as codec
#import MP4 as codec
#import IPP_compressor as codec

# Original video frames (PNG format) with file-names
# f"{video}_{frame_number:03d}.png".
video = "/tmp/original_"
if config.transform == "DWT" or config.transform == "LP":
    reconstructed_video = video + "0_reconstructed_"
else:
    reconstructed_video = video + "reconstructed_"

# Number of frames to process.
n_frames = 60

# Frames Per Second.
FPS = 30

for q_step in range(41, 42, 1):
#for q_step in range(21, 42, 3):

    codec.encode(video, n_frames, q_step)
    kbps, bpp, n_bytes = codec.compute_br(video, FPS, frame.get_frame_shape(video), n_frames)
    _distortion = distortion.AMSE(video, reconstructed_video, n_frames)
    print("Q_step:", q_step, "BPP:", bpp, "KBPS:", kbps, "Average AMSE:", _distortion)
