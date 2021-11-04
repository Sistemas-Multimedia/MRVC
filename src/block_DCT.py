''' MRCV/block_DCT.py '''

import numpy as np
import scipy.fftpack
import deadzone_quantizer as Q
import information
import distortion

def analyze_block(block):
    '''(Forward) DCT block transform.'''
    return scipy.fftpack.dct(scipy.fftpack.dct(block, norm="ortho", axis=0), norm="ortho", axis=1)

def synthesize_block(block):
    '''Inverse DCT block transform.'''
    return scipy.fftpack.idct(scipy.fftpack.idct(block, norm="ortho", axis=1), norm="ortho", axis=0)

def analyze_image(image, block_y_side, block_x_side):
    '''DCT image transform by blocks.'''
    blocks_in_y = image.shape[0]//block_y_side
    blocks_in_x = image.shape[1]//block_x_side
    image_DCT = np.empty_like(image, dtype=np.float32)
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            block = image[y*block_y_side:(y+1)*block_y_side,
                          x*block_x_side:(x+1)*block_x_side]
            DCT_block = analyze_block(block)
            image_DCT[y*block_y_side:(y+1)*block_y_side,
                      x*block_x_side:(x+1)*block_x_side] = DCT_block
    return image_DCT

def synthesize_image(image_DCT, block_y_side, block_x_side):
    '''Inverse DCT image transform by blocks.'''
    blocks_in_y = image_DCT.shape[0]//block_y_side
    blocks_in_x = image_DCT.shape[1]//block_x_side
    image = np.empty_like(image_DCT, dtype=np.int16)
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            DCT_block = image_DCT[y*block_y_side:(y+1)*block_y_side,
                                  x*block_x_side:(x+1)*block_x_side]
            block = synthesize_block(DCT_block)
            image[y*block_y_side:(y+1)*block_y_side,
                  x*block_x_side:(x+1)*block_x_side] = block
    return image

def get_subbands(image_DCT, block_y_side, block_x_side):
    '''Returns the subband form of <image_DCT> (a decomposition). Notice
that a subband is form by the coefficients that are in the same
position in each block of <image_DCT>.

    '''
    blocks_in_y = image_DCT.shape[0]//block_y_side
    blocks_in_x = image_DCT.shape[1]//block_x_side    
    decomposition = np.empty_like(image_DCT)
    for y in range(block_y_side):
        for x in range(block_x_side):
            decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                          x*blocks_in_x:(x+1)*blocks_in_x] = image_DCT[y::block_y_side, x::block_x_side]
    return decomposition

def get_blocks(decomposition, block_y_side, block_x_side):
    '''Returns the block form of <decomposition> (a DCT-ed image by
blocks). Notice that each block is form the the coefficients that are
in the same position of each subband of the input decomposition.

    '''
    blocks_in_y = decomposition.shape[0]//block_y_side
    blocks_in_x = decomposition.shape[1]//block_x_side    
    image_DCT = np.empty_like(decomposition)
    for y in range(block_y_side):
        for x in range(block_x_side):
            image_DCT[y::block_y_side, x::block_x_side] = decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                                                        x*blocks_in_x:(x+1)*blocks_in_x]
    return image_DCT

def _compute_variances(image_DCT, block_y_side, block_x_side):
    '''Compute the variance of each coefficient of a block, or in other
words, compute the variance of each subband.'''
    variances = np.empty(shape=(block_y_side, block_x_side), dtype=np.double)
    for y in range(block_y_side):
        for x in range(block_x_side):
            variances[y, x] = np.var(image_DCT[y::block_y_side, x::block_x_side])
    return variances

def compute_variances(decomposition, block_y_side, block_x_side):
    '''Compute the variance of each subband of <decomposition>.'''
    variances = np.empty(shape=(block_y_side, block_x_side), dtype=np.double)
    blocks_in_y = decomposition.shape[0]//block_y_side
    blocks_in_x = decomposition.shape[1]//block_x_side
    for y in range(block_y_side):
        for x in range(block_x_side):
            subband = decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                    x*blocks_in_x:(x+1)*blocks_in_x]
            variances[y, x] = np.var(subband)
    return variances

def compute_max_min(decomposition, block_y_side, block_x_side):
    '''Compute the dynamic range of each subband of <decomposition>.'''
    max_ = np.empty(shape=(block_y_side, block_x_side), dtype=np.double)
    min_ = np.empty(shape=(block_y_side, block_x_side), dtype=np.double)
    blocks_in_y = decomposition.shape[0]//block_y_side
    blocks_in_x = decomposition.shape[1]//block_x_side
    for y in range(block_y_side):
        for x in range(block_x_side):
            subband = decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                    x*blocks_in_x:(x+1)*blocks_in_x]
            max_[y, x] = np.max(subband)
            min_[y, x] = np.min(subband)
    return max_, min_
    
def quantize(decomposition, Q_steps):
    '''Quantize <decomposition> using <Q_steps>, a matrix of
quantization steps.'''
    block_y_side = Q_steps.shape[0]
    block_x_side = Q_steps.shape[1]
    N_components = Q_steps.shape[2]
    blocks_in_y = decomposition.shape[0]//block_y_side
    blocks_in_x = decomposition.shape[1]//block_x_side    
    quantized_decomposition = np.empty_like(decomposition, dtype=np.int16)

    for y in range(block_y_side):
        for x in range(block_x_side):
            for c in range(N_components):
                subband_component = decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                                  x*blocks_in_x:(x+1)*blocks_in_x,
                                                  c]
                quantized_subband_component = Q.quantize(subband_component, Q_steps[y, x, c])
                quantized_decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                        x*blocks_in_x:(x+1)*blocks_in_x,
                                        c] = quantized_subband_component
    #for y in range(blocks_in_y):
    #    for x in range(blocks_in_x):
    #        block_DCT = image_DCT[y*block_y_side:(y+1)*block_y_side,
    #                              x*block_x_side:(x+1)*block_x_side]
    #        quantized_block_DCT = Q.quantize(block_DCT, Q_steps[y,x])
    #        quantized_image_DCT[y*block_y_side:(y+1)*block_y_side,
    #                            x*block_x_side:(x+1)*block_x_side] = quantized_block_DCT
    #return quantized_image_DCT
    return quantized_decomposition

def dequantize(quantized_decomposition, Q_steps):
    '''De-quantize <quantized_decomposition> using <Q_steps>, a matrix of
quantization steps.

    '''
    block_y_side = Q_steps.shape[0]
    block_x_side = Q_steps.shape[1]
    N_components = Q_steps.shape[2]
    blocks_in_y = quantized_decomposition.shape[0]//block_y_side
    blocks_in_x = quantized_decomposition.shape[1]//block_x_side    
    dequantized_decomposition = np.empty_like(quantized_decomposition, dtype=np.int16)

    for y in range(block_y_side):
        for x in range(block_x_side):
            for c in range(N_components):
                quantized_subband_component = quantized_decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                                                      x*blocks_in_x:(x+1)*blocks_in_x,
                                                                      c]
                dequantized_subband_component = Q.dequantize(quantized_subband_component, Q_steps[y, x, c])
                dequantized_decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                          x*blocks_in_x:(x+1)*blocks_in_x,
                                          c] = dequantized_subband_component
    
    #for y in range(blocks_in_y):
    #    for x in range(blocks_in_x):
    #        quantized_block_DCT = quantized_image_DCT[y*block_y_side:(y+1)*block_y_side,
    #                                                  x*block_x_side:(x+1)*block_x_side]
    #        dequantized_block_DCT = Q.dequantize(quantized_block_DCT, Q_steps[y,x])
    #        #dequantized_block = block_synthesize(dequantized_block_DCT)
    #        dequantized_image_DCT[y*block_y_side:(y+1)*block_y_side,
    #                              x*block_x_side:(x+1)*block_x_side] = dequantized_block_DCT#.astype(np.int16)
    #return dequantized_image_DCT
    return dequantized_decomposition

def uniform_quantize(decomposition, block_y_side, block_x_side, N_components, Q_step):
    '''Quantize <decomposition> with the same <Q_step>.'''
    Q_steps = np.full(shape=(block_y_side, block_x_side, N_components), fill_value=Q_step)
    quantized_decomposition = quantize(decomposition, Q_steps)
    return quantized_decomposition

def uniform_dequantize(quantized_decomposition, block_y_side, block_x_side, N_components, Q_step):
    '''De-quantize <quantized_decomposition> with the same <Q_step>.

    '''
    Q_steps = np.full(shape=(block_y_side, block_x_side, N_components), fill_value=Q_step)
    dequantized_decomposition = dequantize(quantized_decomposition, Q_steps)
    return dequantized_decomposition

def compute_slopes(decomposition, block_y_side, block_x_side, Q_step):
    '''Using a uniform quantization step <Q_step>, this method quantize
<decomposition> returns the estimated (using the entropy) slope of
each subband.

    '''
    blocks_in_y = decomposition.shape[0]//block_y_side
    blocks_in_x = decomposition.shape[1]//block_x_side
    slopes = np.empty(shape=(block_y_side, block_x_side), dtype=np.float)

    for y in range(block_y_side):
        for x in range(block_x_side):
            subband = decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                    x*blocks_in_x:(x+1)*blocks_in_x]
            RD_point_for_Q_step_one = (information.entropy(subband.flatten().astype(np.int16)), 0)
            quantized_subband = Q.quantize(subband, Q_step)
            dequantized_subband = Q.dequantize(quantized_subband, Q_step)
            current_RD_point = (information.entropy(quantized_subband.flatten()), distortion.MSE(subband, dequantized_subband))
            if (RD_point_for_Q_step_one[0] - current_RD_point[0]) == 0:
                slopes[y, x] = 0
            else:
                slopes[y, x] = current_RD_point[1] / (RD_point_for_Q_step_one[0] - current_RD_point[0])

    return slopes

def find_optimal_Q_steps(decomposition, block_y_side, block_x_side, Q_step):
    '''Find the optimal quantization steps for <decomposition>. Scalar
<Q_step> is used to find median slope after a uniform
quantization. Then for those subbands with a smaller slope than the
median, the quantization step is increased until this condition is
false, and viceversa.

    '''
    slopes = compute_slopes(decomposition, block_y_side, block_x_side, Q_step)
    #target_slope = np.median(slopes)
    target_slope = slopes[0][0]
    Q_steps = np.full(shape=(block_y_side, block_x_side), fill_value=Q_step, dtype=np.uint)
    blocks_in_y = decomposition.shape[0]//block_y_side
    blocks_in_x = decomposition.shape[1]//block_x_side

    for y in range(block_y_side):
        print(f"{y}/{block_y_side-1}", end=' ')
        for x in range(block_x_side):
            while slopes[y, x] > target_slope:
                new_Q_step= Q_steps[y,x] - 1
                if new_Q_step <= 0:
                    break
                subband = decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                        x*blocks_in_x:(x+1)*blocks_in_x]
                RD_point_for_Q_step_one = (information.entropy(subband.flatten().astype(np.int16)), 0)
                quantized_subband = Q.quantize(subband, new_Q_step)
                dequantized_subband = Q.dequantize(quantized_subband, new_Q_step)
                # Remember that the DCT is orthonormal, i.e., energy
                # preserving
                current_RD_point = (information.entropy(quantized_subband.flatten()), distortion.MSE(subband, dequantized_subband))
                current_slope = slopes[y, x]
                if (RD_point_for_Q_step_one[0] - current_RD_point[0]) == 0:
                    slopes[y,x] = 0
                else:
                    slopes[y,x] = current_RD_point[1] / (RD_point_for_Q_step_one[0] - current_RD_point[0])
                if current_slope == slopes[y, x]:
                    break
                Q_steps[y, x] = new_Q_step

            while slopes[y, x] < target_slope:
                new_Q_step = Q_steps[y,x] + 1
                subband = decomposition[y*blocks_in_y:(y+1)*blocks_in_y,
                                        x*blocks_in_x:(x+1)*blocks_in_x]
                RD_point_for_Q_step_one = (information.entropy(subband.flatten().astype(np.int16)), 0)
                quantized_subband = Q.quantize(subband, new_Q_step)
                dequantized_subband = Q.dequantize(quantized_subband, new_Q_step)
                current_RD_point = (information.entropy(quantized_subband.flatten()), distortion.MSE(subband, dequantized_subband))
                current_slope = slopes[y,x]
                if (RD_point_for_Q_step_one[0] - current_RD_point[0]) == 0:
                    slopes[y, x] = 0
                else:
                    slopes[y, x] = current_RD_point[1] / (RD_point_for_Q_step_one[0] - current_RD_point[0])
                if current_slope == slopes[y, x]:
                    break
                Q_steps[y,x] = new_Q_step
    return Q_steps, slopes

##########################33

def _find_optimal_Q_steps(image_DCT, block_y_side, block_x_side, Q_steps, current_slopes, target_slope):
    '''Quantize the DCT <image> using a quantization step (to compute)
that generates approximately the same RD-slope for all the
blocks. First, the "master" <Q_step> is used to quantize all the
coefficients and the mean RD-slope is computed. Then, those blocks
with smaller RD-slope increase their quantization step until this
condition is false, and viceversa. The <image> is not quantized.

    '''
    blocks_in_y = image_DCT.shape[0]//block_y_side
    blocks_in_x = image_DCT.shape[1]//block_x_side
    slopes = np.copy(current_slopes)

    # Adjust the quantization step of those blocks with a slope
    # different to <median_slope>.
    for y in range(blocks_in_y):
        print(f"{y}/{blocks_in_y-1}", end=' ')
        for x in range(blocks_in_x):
            while slopes[y,x] > target_slope:
                new_Q_step = Q_steps[y,x] - 1
                if new_Q_step <= 0:
                    break
                block_DCT = image_DCT[y*block_y_side:(y+1)*block_y_side,
                                      x*block_x_side:(x+1)*block_x_side]
                #block_DCT = block_analyze(block)
                RD_point_for_Q_step_one = (information.entropy(block_DCT.flatten().astype(np.int16)), 0)
                quantized_block_DCT = Q.quantize(block_DCT, new_Q_step)
                dequantized_block_DCT = Q.dequantize(quantized_block_DCT, new_Q_step)
                #dequantized_block = block_synthesize(dequantized_block_DCT)
                current_RD_point = (information.entropy(quantized_block_DCT.flatten()), distortion.MSE(block_DCT, dequantized_block_DCT))
                current_slope = slopes[y,x]
                if (RD_point_for_Q_step_one[0] - current_RD_point[0]) == 0:
                    slopes[y,x] = 0
                else:
                    slopes[y,x] = current_RD_point[1] / (RD_point_for_Q_step_one[0] - current_RD_point[0])
                if current_slope == slopes[y,x]:
                    break
                Q_steps[y,x] = new_Q_step

            while slopes[y,x] < target_slope:
                new_Q_step = Q_steps[y,x] + 1
                #if new_Q_step > 64:
                #    break
                block_DCT = image_DCT[y*block_y_side:(y+1)*block_y_side,
                                      x*block_x_side:(x+1)*block_x_side]
                #block_DCT = block_analyze(block)
                RD_point_for_Q_step_one = (information.entropy(block_DCT.flatten().astype(np.int16)), 0)
                quantized_block_DCT = Q.quantize(block_DCT, new_Q_step)
                dequantized_block_DCT = Q.dequantize(quantized_block_DCT, new_Q_step)
                #dequantized_block = block_synthesize(dequantized_block_DCT)
                current_RD_point = (information.entropy(quantized_block_DCT.flatten()), distortion.MSE(block_DCT, dequantized_block_DCT))
                current_slope = slopes[y,x]
                if (RD_point_for_Q_step_one[0] - current_RD_point[0]) == 0:
                    slopes[y,x] = 0
                else:
                    slopes[y,x] = current_RD_point[1] / (RD_point_for_Q_step_one[0] - current_RD_point[0])
                if current_slope == slopes[y,x]:
                    break
                Q_steps[y,x] = new_Q_step

    '''
    # Quantize the image (in the DCT domain).
    quantized_image_DCT = np.empty_like(image)
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            block = image[y*block_y_side:(y+1)*block_y_side,
                          x*block_x_side:(x+1)*block_x_side]
            block_DCT = block_analyze(block)
            quantized_block_DCT = Q.quantize(block_DCT, Q_steps[y,x])
            quantized_image_DCT[y*block_y_side:(y+1)*block_y_side,
                                x*block_x_side:(x+1)*block_x_side] = quantized_block_DCT
            #dequantized_block_DCT = Q.dequantize(quantized_block_DCT, Q_steps[y,x])
            #dequantized_block = inverse_block_transform(dequantized_block_DCT)
            #quantized_image[y*block_y_side:(y+1)*block_y_side,
            #      x*block_x_side:(x+1)*block_x_side] = dequantized_block
    '''
    return Q_steps, slopes

