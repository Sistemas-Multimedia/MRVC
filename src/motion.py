''' MRVC/motion.py '''

import cv2
import numpy as np
import config
import matplotlib
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)
#logging.basicConfig(format="[%(filename)s:%(lineno)s %(funcName)s()] %(message)s")
#logger.setLevel(logging.CRITICAL)
#logger.setLevel(logging.ERROR)
logger.setLevel(logging.WARNING)
#logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)

###########################################################################
# OF section. See:                                                        #
# https://www.geeksforgeeks.org/opencv-the-gunnar-farneback-optical-flow/ #
###########################################################################

# Number of levels of the gaussian pyramid used in the Farneback's
# optical flow computation algorith (OFCA). This value controls the
# search area size.
OF_LEVELS = 3
print("OFCA: default number of levels =", OF_LEVELS)

# Window (squared) side used in the Farneback's OFCA. This value controls the
# coherence of the OF.
OF_WINDOW_SIDE = 33
print(f"OFCA: default window size = {OF_WINDOW_SIDE}x{OF_WINDOW_SIDE}")

# Number of iterations of the Farneback's OFCA. This value controls
# the accuracy of the OF.
OF_ITERS = 3
print(f"OFCA: default number of iterations =", OF_ITERS)

# Signal extension mode used in the OFCA. See https://docs.opencv.org/3.4/d2/de8/group__core__array.html
#ofca_extension_mode = cv2.BORDER_CONSTANT
#ofca_extension_mode = cv2.BORDER_WRAP
#ofca_extension_mode = cv2.BORDER_DEFAULT
ofca_extension_mode = cv2.BORDER_REPLICATE
#ofca_extension_mode = cv2.BORDER_REFLECT
#ofca_extension_mode = cv2.BORDER_REFLECT_101
#ofca_extension_mode = cv2.BORDER_TRANSPARENT
#ofca_extension_mode = cv2.BORDER_REFLECT101
#ofca_extension_mode = BORDER_ISOLATED
print("OFCA: extension mode =", ofca_extension_mode)

#POLY_N = 5
#POLY_SIGMA = 1.1
POLY_N = 7
POLY_SIGMA = 1.5
print("OFCA: default poly_n", POLY_N)
print("OFCA: default poly_sigma", POLY_SIGMA)

def full_search_block_based_ME(P, R, block_side=16, max_abs_motion=8):
    
    def local_search(by, bx):
        errors_by_search_area = np.empty((2*max_abs_motion + 1, 2*max_abs_motion + 1))
        for ry in range(-max_abs_motion, max_abs_motion + 1):
            for rx in range(-max_abs_motion, max_abs_motion + 1):
                R_block = extended_R[by*block_side + ry + max_abs_motion:
                                    (by + 1)*block_side + ry + max_abs_motion,
                                    bx*block_side + rx + max_abs_motion:
                                    (bx + 1)*block_side + rx + max_abs_motion]
                #show_frame(R_block, f"R ({by} {bx} {ry} {rx} {by*block_side + ry + max_abs_motion}:{(by + 1)*block_side + ry + max_abs_motion}, {bx*block_side + rx + max_abs_motion}:{(bx + 1)*block_side + rx + max_abs_motion})")
                P_block = P[by*block_side : (by + 1)*block_side, bx*block_side : (bx + 1)*block_side]
                #show_frame(P_block, f"P ({by*block_side}:{(by + 1)*block_side},{bx*block_side}:{(bx + 1)*block_side})")
                #errors_in_search_area = np.abs(R_block - P_block)
                #error_by_block = np.sum(errors_in_search_area)
                error = R_block.astype(np.float32) - P_block
                errors_in_search_area = error*error
                error_by_block = np.average(errors_in_search_area)
                #show_frame(errors_in_search_area, f"by={by} bx={bx} ry={ry} rx={rx} error={error_by_block}")
                errors_by_search_area[ry + max_abs_motion, rx + max_abs_motion] = error_by_block
                #show_frame(errors_by_search_area, "errors")
        mv_index = np.argmin(errors_by_search_area)
        if errors_by_search_area[max_abs_motion, max_abs_motion] == errors_by_search_area[0, 0]:
            MV_y, MV_x = 0, 0
        else:
            MV_y = mv_index // (2*max_abs_motion + 1) - max_abs_motion
            MV_x = mv_index  % (2*max_abs_motion + 1) - max_abs_motion
        #print("index=", mv_index, "y=", MV_y, "x=", MV_x)
        #print(errors_by_search_area.astype(np.int))
        return MV_y, MV_x

    assert max_abs_motion > 0
    extended_R = cv2.copyMakeBorder(R, max_abs_motion, max_abs_motion, max_abs_motion, max_abs_motion, cv2.BORDER_REPLICATE) 
    extended_R[max_abs_motion : R.shape[0] + max_abs_motion,
               max_abs_motion : R.shape[1] + max_abs_motion] = R
    #show_frame(extended_R, "extended R")
    blocks_in_y = P.shape[0]//block_side
    blocks_in_x = P.shape[1]//block_side
    MVs = np.zeros((blocks_in_y, blocks_in_x, 2), dtype=np.int8)
    #print(blocks_in_y, blocks_in_x)
    for by in range(blocks_in_y):
        for bx in range(blocks_in_x):
            MV_y, MV_x = local_search(by, bx)
            MVs[by, bx] = (MV_x, MV_y)
    return MVs

def Farneback_ME(predicted:np.ndarray,
             reference:np.ndarray,
             initial_MVs:np.ndarray=None,
             levels:int=OF_LEVELS,
             wside:int=OF_WINDOW_SIDE,
             iters:int=OF_ITERS,
             poly_n:float=POLY_N,
             poly_sigma:float=POLY_SIGMA) -> np.ndarray:
    logger.info(f"estimate: levels={levels} wside={wside} iters={iters} poly_n={poly_n} poly_sigma={poly_sigma}")
    MVs = cv2.calcOpticalFlowFarneback(
        prev=predicted,
        next=reference,
        flow=initial_MVs,
        pyr_scale=0.5,
        levels=levels,
        winsize=wside,
        iterations=iters,
        poly_n=5,
        poly_sigma=1.2,
        flags=cv2.OPTFLOW_USE_INITIAL_FLOW | cv2.OPTFLOW_FARNEBACK_GAUSSIAN)
    return MVs

def make_prediction(reference: np.ndarray, MVs: np.ndarray) -> np.ndarray:
    height, width = MVs.shape[:2]
    map_x = np.tile(np.arange(width), (height, 1))
    map_y = np.swapaxes(np.tile(np.arange(height), (width, 1)), 0, 1)
    map_xy = (MVs + np.dstack((map_x, map_y))).astype('float32')
    #map_xy = (np.rint(MVs) + np.dstack((map_x, map_y)).astype(np.float32)) # OJO RINT
    return cv2.remap(reference, map_xy, None, interpolation=cv2.INTER_LINEAR, borderMode=ofca_extension_mode)
    #return cv2.remap(reference, map_xy, None, interpolation=cv2.INTER_NEAREST, borderMode=ofca_extension_mode)
    
    #return cv2.remap(reference, cv2.convertMaps(map_x, map_y, dstmap1type=cv2.CV_16SC2), interpolation=cv2.INTER_LINEAR, borderMode=ofca_extension_mode)
    #return cv2.remap(reference, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=ofca_extension_mode)

def colorize(MVs):
    hsv = np.zeros((MVs.shape[0], MVs.shape[1], 3), dtype=np.uint8)
    hsv[...,1] = 255
    mag, ang = cv2.cartToPolar(MVs[...,0], MVs[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return rgb

def full_search_dense_ME(predicted, reference, search_range=32, overlapping_area_side=17):
    extended_reference = np.zeros((reference.shape[0] + search_range, reference.shape[1] + search_range))
    assert overlapping_area_side % 2 != 0 # This a requirement of cv.GaussianBLur
    extended_reference[search_range//2:reference.shape[0]+search_range//2,
                       search_range//2:reference.shape[1]+search_range//2] = reference
    flow = np.zeros((predicted.shape[0], predicted.shape[1], 2), dtype=np.int8)
    min_error = np.full((predicted.shape[0], predicted.shape[1]), 255, dtype=np.uint8)
    for y in range(search_range):
        print(f"{y}/{search_range-1}", end='\r')
        for x in range(search_range):
            error = extended_reference[y : predicted.shape[0] + y,
                                       x : predicted.shape[1] + x] - predicted
            a_error = abs(error) # Ojo probar MSE
            blur_a_error = cv2.GaussianBlur(a_error, (overlapping_area_side, overlapping_area_side), 0).astype(np.int)
            which_min = blur_a_error <= min_error
            flow[:,:,0] = np.where(which_min, x-search_range//2, flow[:,:,0])
            flow[:,:,1] = np.where(which_min, y-search_range//2, flow[:,:,1])
            min_error = np.minimum(min_error, blur_a_error)
    return flow.astype(np.float)

def show_vectors(flow, dpi=150, title=None):
    #plt.figure.set_dpi(200)
    plt.figure(dpi=dpi)
    plt.quiver(flow[..., 0][::-1], flow[..., 1])
    plt.title(title, fontsize=10)
    plt.show()
