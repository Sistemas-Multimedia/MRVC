''' MRVC/IPP.py '''

import IPP_step
import DWT
import YCoCg

VIDEO_PREFIX = "../sequences/complete_stockholm/"
CODESTREAM_PREFIX = "/tmp/"
DECODED_VIDEO_PREFIX = "/tmp/decoder_"
Q_STEP = 128
N_FRAMES = 16

print("Encoding ...")
IPP_step.encode(video="/tmp/football_", codestream="/tmp/football_codestream_", n_frames=128, q_step=128)
#IPP.encode(video="/tmp/LL", codestream="/tmp/LL", n_frames=16)

print("Decoding ...")
#IPP.decode(codestream="/tmp/LL", video="/tmp/decoded_LL", n_frames=16)
IPP_step.decode(codestream="/tmp/football_codestream_", video="/tmp/football_decoded_", n_frames=128, q_step=128)
