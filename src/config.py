''' MRVC/config.py '''

#q_step = 1
q_step = 54

n_frames = 36

input_video = "/tmp/original_"
codestream = "/tmp/codestream_"
output_video = "/tmp/reconstructed_"

n_levels = 3

fps = 30

wavelet = "haar"
#wavelet = "db5"
#wavelet = "bior3.5"

extension_mode = "periodization" # Gets the minimal number of coefficients
#extension_mode = "symmetric" # Default
#extension_mode = "constant"
#extension_mode = "reflect"
#extension_mode = "periodic"
#extension_mode = "smooth"
#extension_mode = "antisymmetric"
#extension_mode = "antireflect"

#optical_flow_pyramid_levels = 3
optical_flow_pyramid_levels = 5

optical_flow_window_size = 7
#optical_flow_window_size = 5

optical_flow_interations = 3
#optical_flow_interations = 5

print("Quantization step =", q_step)
print("Number of frames to encode =", n_frames)
print("Original video =", input_video)
print("Codestream =", codestream)
print("Reconstructed video =", output_video)
print("Number of spatial resolution levels ", n_levels)
print("Frames per second =", fps)
print("Wavelet =", wavelet)
print("Extension mode=", extension_mode)

