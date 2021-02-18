''' MRVC/stockholm_experiment.py '''

import IPP_step

print("Encoding ...")
#IPP_step.encode(video="/tmp/football_", codestream="/tmp/football_codestream_", n_frames=128, q_step=128)

n_frames = 16
encoder = IPP_step.Encoder(video="/tmp/football_", codestream="/tmp/football_codestream_", q_step=128)
for k in range(1, n_frames):
    encoder.encode_next_frame()

print("Decoding ...")
IPP_step.decode(codestream="/tmp/football_codestream_", video="/tmp/football_decoded_", n_frames=128, q_step=128)
