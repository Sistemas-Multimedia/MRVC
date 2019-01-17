#!/usr/bin/env python3

import numpy as np
import itertools
import sys

sys.path.insert(0, "../..")
from transform.mc.optical.motion import motion_estimation, estimate_frame
from transform.io import image

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def framerate_duplicator(frames):
    ''' Generates n-1 interpolated frames from n base frames.

    Arguments
    ---------

        frames : [[:,:,:]]
            
            List of base frames.

    Returns
    -------

        List of frames including interleaved interpolated frames.

    '''

    output = []

    for curr, next in pairwise(frames):
        output.append(curr)
        flow = motion_estimation(next, curr) / 2
        output.append(estimate_frame(next, flow))
    output.append(frames[-1])

    return output
