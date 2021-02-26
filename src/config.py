''' MRVC/config.py '''

q_step = 32
n_frames = 36
input_video = "/tmp/original_"
codestream = "/tmp/codestream_"
output_video = "/tmp/reconstructed_"
n_levels = 3
fps = 30
wavelet = "haar"
extension_mode = "periodization"

print("Quantization step =", q_step)
print("Number of frames to encode =", n_frames)
print("Original video =", input_video)
print("Codestream =", codestream)
print("Reconstructed video =", output_video)
print("Number of spatial resolution levels ", n_levels)
print("Frames per second =", fps)
print("Wavelet =", wavelet)
print("Extension mode=", extension_mode)

