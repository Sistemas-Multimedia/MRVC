''' MRVC/stockholm_experiment.py '''

import IPP
import argparse
try:
    import argcomplete  # <tab> completion for argparse.
except ImportError:
    print("Unable to import argcomplete")

def int_or_str(text):
    '''Helper function for argument parsing.
    '''
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--input-device", type=int_or_str, help="Input device ID or substring")
parser.add_argument("-o", "--output-device", type=int_or_str, help="Output device ID or substring")
parser.add_argument("-d", "--list-devices", action="store_true", help="Print the available audio devices and quit")

parser.description = __doc__
try:
    argcomplete.autocomplete(parser)
except Exception:
    print("argcomplete not working :-/")
args = parser.parse_known_args()[0]

print("Encoding ...")
IPP.encode(video="/tmp/football_", codestream="/tmp/football_codestream_", n_frames=128)
#IPP.encode(video="/tmp/LL", codestream="/tmp/LL", n_frames=16)

print("Decoding ...")
#IPP.decode(codestream="/tmp/LL", video="/tmp/decoded_LL", n_frames=16)
IPP.decode(codestream="/tmp/football_codestream_", video="/tmp/football_decoded_", n_frames=128)
