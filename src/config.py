''' MRVC/config.py '''

import cv2

# Quantization step.
#q_step = 1
#q_step = 16
q_step = 54
#q_step = 128

# Number of frames to compress.
n_frames = 3
#n_frames = 36

# Input, output, and codestream prefixes.
input_video = "/tmp/original_"
codestream = "/tmp/codestream_"
output_video = "/tmp/reconstructed_"

# Number of levels of the DWT.
#n_levels = 3
n_levels = 3
#n_levels = 7

# DWT filters.
#wavelet = "haar"
#wavelet = "db5"
wavelet = "bior3.5"
#wavelet = "db20"

# Signal extension mode used in the DWT.
dwt_extension_mode = "periodization" # Gets the minimal number of coefficients (important for the compression ratio)
#dwt_extension_mode = "symmetric" # Default
#dwt_extension_mode = "constant"
#dwt_extension_mode = "reflect"
#dwt_extension_mode = "periodic"
#dwt_extension_mode = "smooth"
#dwt_extension_mode = "antisymmetric"
#dwt_extension_mode = "antireflect"

# Number of levels of the gaussian pyramid used in the Farneback's
# optical flow computation algorith (OFCA). This value controls the
# search area size.
#optical_flow_pyramid_levels = 3
optical_flow_pyramid_levels = 5

# Window size used in the Farneback's OFCA. This value controls the
# coherence of the OF.
#optical_flow_window_size = 5
optical_flow_window_size = 33

# Number of iterations of the Farneback's OFCA. This value controls
# the accuracy of the OF.
#optical_flow_iterations = 3
optical_flow_iterations = 5

# Signal extension mode used in the OFCA. See https://docs.opencv.org/3.4/d2/de8/group__core__array.html
ofca_extension_mode = cv2.BORDER_CONSTANT
#ofca_extension_mode = cv2.BORDER_WRAP
#ofca_extension_mode = cv2.BORDER_DEFAULT
#ofca_extension_mode = cv2.BORDER_REPLICATE
#ofca_extension_mode = cv2.BORDER_REFLECT
#ofca_extension_mode = cv2.BORDER_REFLECT_101
#ofca_extension_mode = cv2.BORDER_TRANSPARENT
#ofca_extension_mode = cv2.BORDER_REFLECT101
#ofca_extension_mode = BORDER_ISOLATED

# Frames per second.
fps = 30

def _print():
    print("Quantization step =", q_step)
    print("Number of frames to encode =", n_frames)
    print("Original video =", input_video)
    print("Codestream =", codestream)
    print("Reconstructed video =", output_video)
    print("Number of spatial resolution levels =", n_levels)
    print("Frames per second =", fps)
    print("Wavelet =", wavelet)
    print("DWT extension mode =", dwt_extension_mode)
    print("OFCA extension mode =", ofca_extension_mode)

_print()
