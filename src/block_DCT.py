''' MRCV/block_DCT.py '''

import numpy as np
import scipy.fftpack
import deadzone as Q
import information
import distortion

def block_analyze(block):
    '''(Forward) DCT block transform.'''
    return scipy.fftpack.dct(scipy.fftpack.dct(block, norm="ortho", axis=0), norm="ortho", axis=1)

def block_synthesize(block):
    '''Inverse DCT block transform.'''
    return scipy.fftpack.idct(scipy.fftpack.idct(block, norm="ortho", axis=1), norm="ortho", axis=0)

def analyze(image, block_y_side, block_x_side):
    '''DCT image transform by blocks.'''
    blocks_in_y = image.shape[0]//block_y_side
    blocks_in_x = image.shape[1]//block_x_side
    image_DCT = np.empty_like(image, dtype=np.float32)
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            block = image[y*block_y_side:(y+1)*block_y_side,
                          x*block_x_side:(x+1)*block_x_side]
            DCT_block = block_analyze(block)
            image_DCT[y*block_y_side:(y+1)*block_y_side,
                      x*block_x_side:(x+1)*block_x_side] = DCT_block
    return image_DCT

def synthesize(image_DCT, block_y_side, block_x_side):
    '''Inverse DCT image transform by blocks.'''
    blocks_in_y = image_DCT.shape[0]//block_y_side
    blocks_in_x = image_DCT.shape[1]//block_x_side
    image = np.empty_like(image_DCT, dtype=np.int16)
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            DCT_block = image_DCT[y*block_y_side:(y+1)*block_y_side,
                                  x*block_x_side:(x+1)*block_x_side]
            block = block_synthesize(DCT_block)
            image[y*block_y_side:(y+1)*block_y_side,
                  x*block_x_side:(x+1)*block_x_side] = block
    return image

def quantize(image_DCT, block_y_side, block_x_side, Q_steps):
    '''Quantize all blocks of <image_DCT> using <Q_steps>.'''
    blocks_in_y = image_DCT.shape[0]//block_y_side
    blocks_in_x = image_DCT.shape[1]//block_x_side    
    quantized_image_DCT = np.empty_like(image_DCT, dtype=np.int16)
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            block_DCT = image_DCT[y*block_y_side:(y+1)*block_y_side,
                                  x*block_x_side:(x+1)*block_x_side]
            quantized_block_DCT = Q.quantize(block_DCT, Q_steps[y,x])
            quantized_image_DCT[y*block_y_side:(y+1)*block_y_side,
                                x*block_x_side:(x+1)*block_x_side] = quantized_block_DCT
    return quantized_image_DCT

def constant_quantize(image_DCT, block_y_side, block_x_side, Q_step):
    '''Quantize all blocks of <image_DCT> with the same <Q_step>.'''
    blocks_in_y = image_DCT.shape[0]//block_y_side
    blocks_in_x = image_DCT.shape[1]//block_x_side    
    Q_steps = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=Q_step)
    quantized_image_DCT = quantize(image_DCT, block_y_side, block_x_side, Q_steps)
    '''
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            block = image[y*block_y_side:(y+1)*block_y_side,
                          x*block_x_side:(x+1)*block_x_side]
            block_DCT = block_analyze(block)
            quantized_block_DCT = Q.quantize(block_DCT, Q_step)
            quantized_image_DCT[y*block_y_side:(y+1)*block_y_side,
                                x*block_x_side:(x+1)*block_x_side] = quantized_block_DCT
    '''
    return quantized_image_DCT

def dequantize(quantized_image_DCT, block_y_side, block_x_side, Q_steps):
    '''De-quantize all blocks of the DCT <quantized_image_DCT> using <Q_steps>.

    '''
    blocks_in_y = quantized_image_DCT.shape[0]//block_y_side
    blocks_in_x = quantized_image_DCT.shape[1]//block_x_side    
    dequantized_image_DCT = np.empty_like(quantized_image_DCT, dtype=np.int16)
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            quantized_block_DCT = quantized_image_DCT[y*block_y_side:(y+1)*block_y_side,
                                                      x*block_x_side:(x+1)*block_x_side]
            dequantized_block_DCT = Q.dequantize(quantized_block_DCT, Q_steps[y,x])
            #dequantized_block = block_synthesize(dequantized_block_DCT)
            dequantized_image_DCT[y*block_y_side:(y+1)*block_y_side,
                                  x*block_x_side:(x+1)*block_x_side] = dequantized_block_DCT#.astype(np.int16)
    return dequantized_image_DCT

def constant_dequantize(quantized_image_DCT, block_y_side, block_x_side, Q_step):
    '''De-quantize all blocks of the DCT <quantized_image_DCT> with the
same <Q_step>.

    '''
    blocks_in_y = quantized_image_DCT.shape[0]//block_y_side
    blocks_in_x = quantized_image_DCT.shape[1]//block_x_side
    Q_steps = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=Q_step)
    dequantized_image_DCT = dequantize(quantized_image_DCT, block_y_side, block_x_side, Q_steps)
    '''
    dequantized_image = np.empty_like(quantized_image_DCT, dtype=np.int16)
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            quantized_block_DCT = quantized_image_DCT[y*block_y_side:(y+1)*block_y_side,
                                                      x*block_x_side:(x+1)*block_x_side]
            dequantized_block_DCT = Q.dequantize(quantized_block_DCT, Q_step)
            dequantized_block = block_synthesize(dequantized_block_DCT)
            dequantized_image[y*block_y_side:(y+1)*block_y_side,
                              x*block_x_side:(x+1)*block_x_side] = dequantized_block.astype(np.int16)
    '''
    return dequantized_image_DCT

def get_slopes(image_DCT, block_y_side, block_x_side, Q_step):
    blocks_in_y = image_DCT.shape[0]//block_y_side
    blocks_in_x = image_DCT.shape[1]//block_x_side    
    #quantized_image = constant_quantize(image, block_y_side, block_x_side, Q_step)
    Q_steps = np.full(shape=(blocks_in_y, blocks_in_x), fill_value=Q_step, dtype=np.uint)
    slopes = np.empty(shape=(blocks_in_y, blocks_in_x), dtype=np.float)
    #print(image_DCT.max(), image_DCT.min())
    #print(blocks_in_y, blocks_in_x)
    for y in range(blocks_in_y):
        for x in range(blocks_in_x):
            block_DCT = image_DCT[y*block_y_side:(y+1)*block_y_side,
                                  x*block_x_side:(x+1)*block_x_side]
            #print(y,x,block_DCT.max(),block_DCT.min())
            #block_DCT = block_analyze(block)
            # The RD-slope is computed considering the RD-point for
            # lossless coding and the RD-point generated by the
            # current cuantization step.
            #print(block_DCT.max(), block_DCT.min())
            RD_point_for_Q_step_one = (information.entropy(block_DCT.flatten().astype(np.int16)), 0)
            #print("1", RD_point_for_Q_step_one)
            quantized_block_DCT = Q.quantize(block_DCT, Q_step)
            dequantized_block_DCT = Q.dequantize(quantized_block_DCT, Q_step)
            #dequantized_block = block_synthesize(dequantized_block_DCT)
            # Notice that if the DCT is orthogonal, the distortion can
            # be also computed in the transform domain.
            current_RD_point = (information.entropy(quantized_block_DCT.flatten()), distortion.MSE(block_DCT, dequantized_block_DCT))
            #print("2", current_RD_point)
            #print(RD_point_for_Q_step_one, current_RD_point)
            if (RD_point_for_Q_step_one[0] - current_RD_point[0]) == 0:
                slopes[y,x] = 0
            else:
                slopes[y,x] = current_RD_point[1] / (RD_point_for_Q_step_one[0] - current_RD_point[0])

    return slopes, Q_steps
    #median_slope = np.median(slopes)
    #return median_slope

def find_optimal_Q_steps(image_DCT, block_y_side, block_x_side, Q_steps, slopes, target_slope):
    '''Quantize the DCT <image> using a quantization step (to compute)
that generates approximately the same RD-slope for all the
blocks. First, the "master" <Q_step> is used to quantize all the
coefficients and the mean RD-slope is computed. Then, those blocks
with smaller RD-slope increase their quantization step until this
condition is false, and viceversa. The <image> is not quantized.

    '''
    blocks_in_y = image_DCT.shape[0]//block_y_side
    blocks_in_x = image_DCT.shape[1]//block_x_side    

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
                if new_Q_step > 64:
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

def compute_variances(image_DCT, block_y_side, block_x_side):
    variances = np.empty(shape=(block_y_side, block_x_side), dtype=np.double)
    for y in range(block_y_side):
        for x in range(block_x_side):
            variances[y, x] = np.var(image_DCT[y::block_y_side, x::block_x_side])
    return variances

def correlate(image_DCT, block_y_side, block_x_side):
    blocks_in_y = image_DCT.shape[0]//block_y_side
    blocks_in_x = image_DCT.shape[1]//block_x_side    
    correlated_image_DCT = np.empty_like(image_DCT)
    for y in range(block_y_side):
        for x in range(block_x_side):
            correlated_image_DCT[y*blocks_in_y:(y+1)*blocks_in_y,
                                 x*blocks_in_x:(x+1)*blocks_in_x] = image_DCT[y::block_y_side, x::block_x_side]
    return correlated_image_DCT

def decorrelate(correlated_image_DCT, block_y_side, block_x_side):
    blocks_in_y = correlated_image_DCT.shape[0]//block_y_side
    blocks_in_x = correlated_image_DCT.shape[1]//block_x_side    
    image_DCT = np.empty_like(correlated_image_DCT)
    for y in range(block_y_side):
        for x in range(block_x_side):
            image_DCT[y::block_y_side, x::block_x_side]= correlated_image_DCT[y*blocks_in_y:(y+1)*blocks_in_y,
                                                                              x*blocks_in_x:(x+1)*blocks_in_x]
    return image_DCT
