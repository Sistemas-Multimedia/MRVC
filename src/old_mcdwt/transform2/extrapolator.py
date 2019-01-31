#!/usr/bin/env python3

import numpy as np
import motion

def extrapolate_frame(base, displacement):
    '''Extrapolate an image based on an image and a constant displacement.

    Arguments
    ---------

        base : [:,:,:]

            Base frame.

        displacement : (x, y)

            Displacement tuple.

    Returns
    -------

        Extrapolated frame.

    '''
    x, y, _ = base.shape
    flow = np.full((x, y, 2), displacement, dtype=np.float32)
    return motion.estimate_frame(base, flow)
