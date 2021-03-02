''' MRVC/compute_br.py '''

import config
import os

sequence_time = config.n_frames/config.fps

def debug_print(*args):
    if __debug__:
        print(args)

total_bytes = 0
bytes_by_level = 0
for k in range(config.n_frames):
    fn = f"{config.codestream}{config.n_levels}_LL{k:03d}.png"
    _bytes = os.path.getsize(fn)
    debug_print(fn, _bytes)
    total_bytes += _bytes
print("bit-rate by level", config.n_levels+1, "=", bytes_by_level*8/sequence_time/1000, "(kbps)")
total_bytes += bytes_by_level

for l in range(config.n_levels, 0, -1):
    bytes_by_level = 0
    for k in range(config.n_frames):
        fn = f"{config.codestream}{l}_LH{k:03d}.png"
        _bytes = os.path.getsize(fn)
        debug_print(fn, _bytes)
        bytes_by_level += _bytes

        fn = f"{config.codestream}{l}_HL{k:03d}.png"
        _bytes = os.path.getsize(fn)
        debug_print(fn, _bytes)
        bytes_by_level += _bytes
        
        fn = f"{config.codestream}{l}_HH{k:03d}.png"
        _bytes = os.path.getsize(fn)
        debug_print(fn, _bytes)
        bytes_by_level += _bytes
    print("bit-rate by level", l, "=", bytes_by_level*8/sequence_time/1000, "(kbps)")
    total_bytes += bytes_by_level

print("total_bytes =", total_bytes)
print("sequence time =", sequence_time, "(s)")
print("bit-rate =", total_bytes*8/sequence_time/1000, "(kbps)")
