''' MRVC/image_IPP_RD.py '''

# Generate a RD curve for the IPP... encoding scheme.

#import image_interpolated_IPP as IPP
import image_IPP as IPP
import config
import distortion
import frame

number_of_frames = 5
prefix = "/tmp"
video = prefix + "/original_"
codestream = prefix + "/codestream_"
reconstructed = prefix + "/reconstructed_"
FPS = 30
subpixel_accuracy = 1

for q_step in range(30,31):

    IPP.encode(
        video,
        codestream,
        number_of_frames,
        q_step,
        subpixel_accuracy)

    kbps, bpp = IPP.compute_br(
        codestream,
        FPS,
        frame.get_frame_shape(video),
        number_of_frames)
    
    _distortion = distortion.AMSE(
        video,
        f"{video}reconstructed",
        number_of_frames)

    print("RD:", bpp, _distortion)
