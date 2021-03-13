''' MRVC/config.py '''

import cv2

# Number of frames to compress.
n_frames = 5
n_frames = 36
#n_frames = 100
#n_frames = 360
#n_frames = 500

# Input, output, and codestream prefixes.
prefix = "/tmp"
#prefix = "/media/sdc1/Q8L3_LP"
#prefix = "/media/sdc1/Q54L3_DWT"
#prefix = "/media/sdc1"
input_video = f"{prefix}/original_"
codestream = f"{prefix}/codestream_"
output_video = f"{prefix}/reconstructed_"

subpixel_accuracy = 1

# Number of spatial resolution levels
nsrl = 5

# Frames per second.
fps = 30

print(f"config.py: n_frames={n_frames}")
print(f"config.py: input_video={input_video}")
print(f"config.py: codestream={codestream}")
print(f"config.py: output_video={output_video}")
print(f"config.py: nsrl={nsrl} (number of spatial resolution levels)")
print(f"config.py: fps={fps} (frames per second)")
print(f"config.py: subpixel_accuracy={subpixel_accuracy}")
