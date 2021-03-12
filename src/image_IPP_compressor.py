''' MRVC/image_IPP_compressor.py '''

import image_IPP as IPP
import config
import distortion
import frame

print("IPP... encoding")

for q_step in range(50):

    IPP.encode(config.input_video, config.codestream, config.n_frames, q_step)

    kbps, bpp = IPP.compute_br(prefix=config.codestream,
                               frames_per_second=config.fps,
                               frame_shape=frame.get_frame_shape(config.input_video),
                               n_frames=config.n_frames)

    amse = distortion.AMSE(config.input_video, f"{config.input_video}_reconstructed", config.n_frames)

    print(bpp, amse)
