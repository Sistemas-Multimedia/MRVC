''' MRVC/RD_curve.py '''

# Generate a RD curve.

#import debug
import config
import distortion
import image_3 as frame

if config.temporal_codec == "image_IPP":
    import image_IPP as codec
if config.temporal_codec == "image_IPP_adaptive":
    import image_IPP_adaptive as codec
if config.temporal_codec == "MP4":
    import MP4 as codec

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(filename)s:%(lineno)s %(funcName)s() %(levelname)s] %(message)s")
##logger.setLevel(logging.CRITICAL)
##logger.setLevel(logging.ERROR)
#logger.setLevel(logging.WARNING)
logger.setLevel(logging.INFO)
##logger.setLevel(logging.DEBUG)
#logging.basicConfig(format="[%(filename)s:%(lineno)s %(levelname)s %(funcName)s()] %(message)s", level=logging.INFO)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--N_frames", type=int, help="Number of frames", default=8)
parser.add_argument("--first_frame", type=int, help="First frame to compress", default=0)
args = parser.parse_args()

# Original video frames (PNG format) with file-names
# f"{video}_{frame_number:03d}.png".
video = "/tmp/original_"
if config.multiresolution_transform == "DWT" or config.multiresolution_transform == "LP":
    reconstructed_video = video + "0_reconstructed_"
else:
    reconstructed_video = video + "reconstructed_"

first_frame = args.first_frame
logging.info(f"first_frame={first_frame}")
    
# Number of frames to process.
n_frames = args.N_frames
logging.info(f"N_frames={n_frames}")

# Frames Per Second.
FPS = 30

def AMSE(x_prefix, y_prefix, first_frame, n_images):
    print(f"AMSE: comparing {x_prefix} and {y_prefix}")
    total_AMSE = 0
    for k in range(n_images):
        x = frame.read(x_prefix, first_frame + k)
        y = frame.read(y_prefix, first_frame + k)
        _AMSE = distortion.MSE(x, y)
        logging.info(f"AMSE of image {k} = {_AMSE}")
        total_AMSE += _AMSE
    _AMSE = total_AMSE/n_images
    logging.info("Average Mean Square Error (entire sequence) =", _AMSE)
    return _AMSE

for q_step in config.Q_steps:

    codec.encode(video, first_frame, n_frames, q_step)
    kbps, bpp, n_bytes = codec.compute_br(video, FPS, frame.get_shape(video), first_frame, n_frames)
    _distortion = AMSE(video, reconstructed_video, first_frame, n_frames)
    # Don't use logging here!
    print("Q_step:", q_step, "BPP:", bpp, "KBPS:", kbps, "Average AMSE:", _distortion)
