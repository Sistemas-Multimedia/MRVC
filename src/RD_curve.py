''' MRVC/image_IPP_RD.py '''

# Generate a RD curve.

import debug
import config
import distortion
import image_3 as frame

# --> Select below the codec. <--
#import image_interpolated_IPP as codec
import image_IPP as codec
#import image_IPP_adaptive as codec
#import image_IPP_quantized_prediction as codec
#import image_IPP_quantized_residue as codec
#import MP4 as codec
#import IPP_compressor as codec

# Original video frames (PNG format) with file-names
# f"{video}_{frame_number:03d}.png".
video = "/tmp/original_"
if config.multiresolution_transform == "DWT" or config.multiresolution_transform == "LP":
    reconstructed_video = video + "0_reconstructed_"
else:
    reconstructed_video = video + "reconstructed_"

# Number of frames to process.
n_frames = 30

# Frames Per Second.
FPS = 30

def AMSE(x_prefix, y_prefix, n_images):
    print(f"AMSE: comparing {x_prefix} and {y_prefix}")
    total_AMSE = 0
    for k in range(n_images):
        x = frame.read(x_prefix, k)
        y = frame.read(y_prefix, k)
        _AMSE = distortion.MSE(x, y)
        debug.print(f"AMSE of image {k} = {_AMSE}")
        total_AMSE += _AMSE
    _AMSE = total_AMSE/n_images
    debug.print("Average Mean Square Error (entire sequence) =", _AMSE)
    return _AMSE

#for q_step in range(41, 42, 1):
for q_step in range(21, 42, 3):

    codec.encode(video, n_frames, q_step)
    kbps, bpp, n_bytes = codec.compute_br(video, FPS, frame.get_shape(video), n_frames)
    _distortion = AMSE(video, reconstructed_video, n_frames)
    print("Q_step:", q_step, "BPP:", bpp, "KBPS:", kbps, "Average AMSE:", _distortion)
