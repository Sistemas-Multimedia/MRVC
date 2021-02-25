''' MRVC/compute_br.py '''

import os

codestream = "/tmp/football_codestream_"
n_frames = 32
n_levels = 3
fps = 30

total_bytes = 0
for k in range(n_frames):
    fn = f"{codestream}{n_levels}_LL{k:03d}.png"
    _bytes = os.path.getsize(fn)
    print(fn, _bytes)
    total_bytes += _bytes

for l in range(n_levels, 0, -1):
    for k in range(n_frames):
        fn = f"{codestream}{l}_LH{k:03d}.png"
        _bytes = os.path.getsize(fn)
        print(fn, _bytes)
        total_bytes += _bytes

        fn = f"{codestream}{l}_HL{k:03d}.png"
        _bytes = os.path.getsize(fn)
        print(fn, _bytes)
        total_bytes += _bytes
        
        fn = f"{codestream}{l}_HH{k:03d}.png"
        _bytes = os.path.getsize(fn)
        print(fn, _bytes)
        total_bytes += _bytes

print("total_bytes =", total_bytes)
sequence_time = n_frames/fps
print("sequence time =", sequence_time, "(s)")
print("bit-rate =", total_bytes*8/sequence_time/1000, "(kbps)")
