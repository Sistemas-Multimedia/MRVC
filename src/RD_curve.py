''' MRVC/image_IPP_RD.py '''

# Generate a RD curve.

import distortion
import frame

# --> Select below the codec. <--
#import image_interpolated_IPP as IPP
#import image_IPP as IPP
import image_IPP_adaptive as IPP
#import MP4 as IPP

# Original video frames (PNG format) with file-names
# f"{video}_{frame_number:03d}.png".
video = "/tmp/original_"

# Number of frames to process.
n_frames = 30

# Frames Per Second.
FPS = 30

for q_step in range(41, 42, 1):
#for q_step in range(21, 42, 3):

    IPP.encode(video, n_frames, q_step)

    kbps, bpp = IPP.compute_br(video, FPS,
                               frame.get_frame_shape(video), n_frames)
    
    _distortion = distortion.AMSE(video, f"{video}reconstructed_",
                                  n_frames)

    print("Q_step:", q_step, "BPP:", bpp, "KBPS:", kbps, "Average AMSE:", _distortion)
