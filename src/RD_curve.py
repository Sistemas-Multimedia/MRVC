''' MRVC/image_IPP_RD.py '''

# Generate a RD curve.

import distortion
import frame

# --> Select below the codec. <--
#import image_interpolated_IPP as IPP
#import image_IPP as IPP
import image_IPP_adaptive as IPP

# Original video frames (PNG format) with file-names
# f"{video}_{frame_number:03d}.png".
video = "/tmp/original_"

# Number of frames to process.
number_of_frames = 50

# Frames Per Second.
FPS = 30

for q_step in range(21, 42, 1):

    IPP.encode(video, number_of_frames, q_step)

    kbps, bpp = IPP.compute_br(video, FPS,
                               frame.get_frame_shape(video), number_of_frames)
    
    _distortion = distortion.AMSE(video, f"{video}reconstructed_",
                                  number_of_frames)

    print("BPP:", bpp)
    print("KBPS:", kbps)
    print("Average AMSE:", _distortion)
