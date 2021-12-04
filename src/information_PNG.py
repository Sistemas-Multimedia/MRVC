'''Information estimation.'''

import numpy as np
import math
import logging
import os

import information
import image_3 as image

def PNG_BPP(_image, prefix):
    image.write(_image, prefix, 0)
    fn = prefix + "000.png"
    codestream_length = os.path.getsize(fn)
    BPP = (8*codestream_length)/np.size(_image)
    if __debug__:
        __image = image.read(prefix, 0)
        return BPP, __image
    else:
        return BPP, None

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
    
