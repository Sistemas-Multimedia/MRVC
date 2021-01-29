#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

''' MRVC/IO image sequence. '''

import zlib
import numpy as np
import struct
import math
try:
    import argcomplete  # <tab> completion for argparse.
except ImportError:
    print("Unable to import argcomplete")

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--input", type=str, help="Prefix path input sequence")
parser.add_argument("-o", "--output", type=str, help="Prefix path output sequence")
    
class Deflate():
    def __init__(self):
        if __debug__:
            print("IO.__init__")
        else:
            pass

    def decode_frame(self, prefix):
        fn = f"{prefix}.png"
        frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED) # [rows, columns, components]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.array(frame)
        frame = frame.astype(np.float32) - 32768.0
        return frame

    def encode_frame(self, frame, prefix):
        frame = frame.astype(np.float32)
        frame += 32768.0
        frame = frame.astype(np.uint16)
        cv2.imwrite(f"{prefix}.png", frame)

    def encode_seq(self, prefix, length):
        for i in range(length):
            self.encode_frame(self.decode_frame(prefix), prefix)
   
class Deflate__verbose(Deflate):
    pass

if __name__ == "__main__":
    deflate.parser.description = __doc__
    try:
        argcomplete.autocomplete(deflate.parser)
    except Exception:
        if __debug__:
            print("argcomplete not working :-/")
        else:
            pass
    deflate.args = deflate.parser.parse_known_args()[0]
    if deflate.args.show_stats or minimal.args.show_samples:
        codec = Deflate__verbose()
    else:
        codec = Deflate()
    try:
        codec.run()
    except KeyboardInterrupt:
        codec.parser.exit("\nInterrupted by user")
