''' MRVC/compute_br.py '''

import config
import os

total_bytes = 0
for k in range(config.n_frames):
    fn = f"{config.codestream}{config.n_levels}_LL{k:03d}.png"
    _bytes = os.path.getsize(fn)
    print(fn, _bytes)
    total_bytes += _bytes

for l in range(config.n_levels, 0, -1):
    for k in range(config.n_frames):
        fn = f"{config.codestream}{l}_LH{k:03d}.png"
        _bytes = os.path.getsize(fn)
        print(fn, _bytes)
        total_bytes += _bytes

        fn = f"{config.codestream}{l}_HL{k:03d}.png"
        _bytes = os.path.getsize(fn)
        print(fn, _bytes)
        total_bytes += _bytes
        
        fn = f"{config.codestream}{l}_HH{k:03d}.png"
        _bytes = os.path.getsize(fn)
        print(fn, _bytes)
        total_bytes += _bytes

print("total_bytes =", total_bytes)
sequence_time = config.n_frames/config.fps
print("sequence time =", sequence_time, "(s)")
print("bit-rate =", total_bytes*8/sequence_time/1000, "(kbps)")
