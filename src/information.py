''' MRVC/rate.py '''

import numpy as np
import math
import debug
import frame
import os

def entropy(sequence_of_symbols):
    value, counts = np.unique(sequence_of_symbols, return_counts = True)
    probs = counts / len(sequence_of_symbols)
    n_classes = np.count_nonzero(probs)
    debug.print("information.entropy: sequence_of_symbols.max() =", sequence_of_symbols.max())
    debug.print("information.entropy: sequence_of_symbols.min() =", sequence_of_symbols.min())
    debug.print("information.entropy: n_clases = ", n_classes)
    #debug.print("information.entropy: probs =", probs)

    if n_classes <= 1:
        return 0

    _entropy = 0.
    for i in probs:
        _entropy -= i * math.log(i, 2)
    debug.print("information.entropy: _entropy =", _entropy)

    return _entropy

def PNG_BPP(image):
    frame.write(image, "/tmp/PNG_BPP_", 0)
    fn = "/tmp/PNG_BPP_000.png"
    codestream_length = os.path.getsize(fn)
    return codestream_length/np.size(image)*8

if __name__ == "__main__":

    sequence = np.array([0,1], dtype=np.uint8)
    print(sequence, entropy(sequence))

    sequence = np.array([0,1,2,3], dtype=np.uint8)
    print(sequence, entropy(sequence))

    sequence = np.array([0,1,1,2,3], dtype=np.uint8)
    print(sequence, entropy(sequence))

    sequence = np.array([0,-1,1,-2,3], dtype=np.uint8)
    print(sequence, entropy(sequence))

    sequence = np.arange(21, dtype=np.uint8)
    print(sequence, entropy(sequence))    

    sequence = np.arange(21, dtype=np.uint8).reshape(3,7)
    print(sequence, entropy(sequence))
    
    sequence = np.arange(21, dtype=np.uint8).reshape(3,7)
    print(sequence, PNG_BPP(sequence))
    
