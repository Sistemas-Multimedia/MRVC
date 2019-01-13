#!/usr/bin/env python
'''
Linear frame interpolation using Bidirectional Block-Based Motion Compensation
'''
import argparse
#from PIL import Image, ImageChops, ImageEnhance, ImageOps
import numpy as np
import pywt

    #Método que implementa la búsqueda en espiral
def local_me_for_block(mv, ref, pred, luby, lubx, rbby, rbbx, by, bx):
    min_error=np.array([0, 1])
    vy=np.array([0, 1])
    vx=np.array([0, 1])
    
    mv_prev_y_by_bx = np.array([mv[PREV], mv[Y_FIELD], mv[by], mv[bx]])
    mv_prev_x_by_bx = np.array([mv[PREV], mv[X_FIELD], mv[by], mv[bx]])
    mv_next_y_by_bx = np.array([mv[NEXT], mv[Y_FIELD], mv[by], mv[bx]])
    mv_next_x_by_bx = np.array([mv[NEXT], mv[X_FIELD], mv[by], mv[bx]])
    
def COMPUTE_ERRORS(_y, _x):
    y=np.array([mv_prev_y_by_bx + _y, mv_next_y_by_bx - _y])
    x=np.array([mv_prev_x_by_bx + _x, mv_next_x_by_bx - _x])
    error=np.array([0, 0])
    
    for num in range(luby, rbby):
        pred_py=np.array([pred[num]])
        for num2 in range(lubx, rbbx):
            error[PREV] += abs(pred_py[num2] - np.array([ref[PREV], ref[py + y[PREV]], [px + x[PREV]]]))
            error[NEXT] += abs(pred_py[num2] - np.array([ref[NEXT], ref[py + y[NEXT]], [px + x[NEXT]]]))

def UPDATE_VECTORS():
    if(error[PREV] <= min_error[PREV]):
        vy[PREV]=y[PREV]
        vx[PREV]=x[PREV]
        min_error[PREV]=error[PREV]

    if(error[NEXT] <= min_error[NEXT]):
        vy[NEXT]=y[NEXT]
        vx[NEXT]=x[NEXT]
        min_error[NEXT]=error[NEXT]
        
    #1. Position (-1,-1). Up - Left.
    COMPUTE_ERRORS(-1,-1)
    
    min_error[PREV]=error[PREV]
    vy[PREV]=y[PREV]
    vx[PREV]=x[PREV]
    
    min_error[NEXT]=error[NEXT]
    vy[NEXT]=y[NEXT]
    vx[NEXT]=x[NEXT]
    
    #2. Position (-1,1). Up - Right.
    COMPUTE_ERRORS(-1,1)
    UPDATE_VECTORS()
    
    #3. Position (1,-1). Down - left.
    COMPUTE_ERRORS(1,-1)
    UPDATE_VECTORS()
    
    #4. Position (1,1). Down - Right.
    COMPUTE_ERRORS(1,1)
    UPDATE_VECTORS()

    #5. Position (-1,0). Up.
    COMPUTE_ERRORS(-1,0)
    UPDATE_VECTORS

    #6. Position (1,0). Down.
    COMPUTE_ERRORS(1,0)
    UPDATE_VECTORS()

    #7. Position (0,1). Right.
    COMPUTE_ERRORS(0,1)
    UPDATE_VECTORS()

    #8. Position (0,-1). Left.
    COMPUTE_ERRORS(0,-1)
    UPDATE_VECTORS()

    #9. Position (0,0). */ {
    COMPUTE_ERRORS(0,0)
    UPDATE_VECTORS()

    mv_prev_y_by_bx=vy[PREV]
    mv_prev_x_by_bx=vx[PREV]
    mv_next_y_by_bx=vy[NEXT]
    mv_next_x_by_bx=vx[NEXT]

	
#local_me_for_image()
def local_me_for_image(mv,ref,pred,block_size,border_size,blocks_in_y,blocks_in_x):

    for by in range(blocks_in_y):
        for bx in range(blocks_in_x):
		
            luby = (by ) * block_size - border_size
            lubx = (bx ) * block_size - border_size
            rbby = (by+1) * block_size - border_size
            rbbx = (bx+1) * block_size - border_size
            
            local_me_for_block(mv, ref, pred, luby, lubx, rbby, rbbx, by, bx)


#me_for_image()-Fastsearch
def me_for_image(mv,ref,pred,pixels_in_y,pixels_in_x,block_size,border_size,subpixel_accuracy,search_range,blocks_in_y,blocks_in_x):

	#5.3
    TEXTURE_INTERPOLATION_FILTER = 'bior2.2'
    MOTION_INTERPOLATION_FILTER = 'haar'
    
    dwt_levels = round(log(search_range)/log(2.0))-1

    pic_dwt_refPrev = pywt.wavedec2(dwtrefprev,TEXTURE_INTERPOLATION_FILTER,dwt_levels)
    pic_dwt_refNext = pywt.wavedec2(dwtrefnext,TEXTURE_INTERPOLATION_FILTER,dwt_levels)
    pic_dwt_pred = pywt.wavedec2(dwtpred,TEXTURE_INTERPOLATION_FILTER,dwt_levels)		

    local_me_for_image(mv,ref,pred,block_size,border_size, desp(blocks_in_y, dwt_levels),desp(blocks_in_x, dwt_levels))

    for l in range(dwt_levels,-1,-1):
	
        Y_l = pixels_in_y/2
        X_l = pixels_in_x/2
        blocks_in_y_l = blocks_in_y/2
        blocks_in_x_l = blocks_in_x/2
        
        pic_dwt_refPrev = pywt.waverec2(pic_dwt_refPrev,TEXTURE_INTERPOLATION_FILTER,1)
        pic_dwt_refNext = pywt.waverec2(pic_dwt_refNext,TEXTURE_INTERPOLATION_FILTER,1)
        pic_dwt_pred = pywt.waverec2(pic_dwt_pred,TEXTURE_INTERPOLATION_FILTER,1)
        
        mv_idwt_refPrevY = pywt.waverec2(dwtmvrefprevy,MOTION_INTERPOLATION_FILTER,1)
        mv_idwt_refNextY = pywt.waverec2(dwtmvrefnexty,MOTION_INTERPOLATION_FILTER,1)
        mv_idwt_refPrevX = pywt.waverec2(dwtmvrefprevx,MOTION_INTERPOLATION_FILTER,1)
        mv_idwt_refNextX = pywt.waverec2(dwtmvrefnextx,MOTION_INTERPOLATION_FILTER,1)
        
        mv_prev_y_by_bx = np.array([mv[PREV], mv[Y_FIELD], mv[by], mv[bx]])
        mv_prev_x_by_bx = np.array([mv[PREV], mv[X_FIELD], mv[by], mv[bx]])
        mv_next_y_by_bx = np.array([mv[NEXT], mv[Y_FIELD], mv[by], mv[bx]])
        mv_next_x_by_bx = np.array([mv[NEXT], mv[X_FIELD], mv[by], mv[bx]])
        
        for by in range(blocks_in_y_l):
            for bx in range(blocks_in_x_l):
                
                mv_prev_y_by_bx *= 2;
                if mv_prev_y_by_bx > search_range:
                    mv_prev_y_by_bx = search_range
                if mv_prev_y_by_bx < -search_range:
                    mv_prev_y_by_bx = -search_range
                    
                mv_next_y_by_bx  *= 2;
                if mv_next_y_by_bx  > search_range:
                    mv_next_y_by_bx  =  search_range
                if mv_next_y_by_bx  < -search_range:
                    mv_next_y_by_bx  = -search_range

                mv_prev_x_by_bx *= 2;
                if mv_prev_x_by_bx > search_range:
                    mv_prev_x_by_bx =  search_range
                if mv_prev_x_by_bx < -search_range:
                    mv_prev_x_by_bx = -search_range
                    
                mv_next_x_by_bx *= 2;
                if mv_next_x_by_bx > search_range:
                    mv_next_x_by_bx =  search_range
                if mv_next_x_by_bx < -search_range:
                    mv_next_x_by_bx = -search_range
                    
        local_me_for_image(mv,ref,pred,block_size,border_size,blocks_in_y_l, blocks_in_x_l)
        
    for l in range(1,subpixel_accuracy+1):

        pic_dwt_refPrev = pywt.waverec2(pic_dwt_refPrev,TEXTURE_INTERPOLATION_FILTER,1)
        pic_dwt_refNext = pywt.waverec2(pic_dwt_refNext,TEXTURE_INTERPOLATION_FILTER,1)
        pic_dwt_pred= pywt.waverec2(pic_dwt_pred,TEXTURE_INTERPOLATION_FILTER,1)

        for by in range(blocks_in_y_l):
            for bx in range(blocks_in_y_l):
                
                mv_prev_y_by_bx *= 2
                if mv_prev_y_by_bx > (search_range<<subpixel_accuracy):
                    mv_prev_y_by_bx = search_range<<subpixel_accuracy
                if mv_prev_y_by_bx < -(search_range<<subpixel_accuracy):
                    mv_prev_y_by_bx = -(search_range<<subpixel_accuracy)

                mv_next_y_by_bx *= 2
                if mv_next_y_by_bx > (search_range<<subpixel_accuracy):
                    mv_next_y_by_bx = search_range<<subpixel_accuracy
                if mv_next_y_by_bx < -(search_range<<subpixel_accuracy):
                    mv_next_y_by_bx = -(search_range<<subpixel_accuracy)

                mv_prev_x_by_bx *= 2
                if mv_prev_x_by_bx > (search_range<<subpixel_accuracy):
                    mv_prev_x_by_bx = (search_range<<subpixel_accuracy)
                if mv_prev_x_by_bx < -(search_range<<subpixel_accuracy):
                    mv_prev_x_by_bx = -(search_range<<subpixel_accuracy)

                mv_next_x_by_bx *= 2
                if mv_next_x_by_bx > (search_range<<subpixel_accuracy):
                    mv_next_x_by_bx = (search_range<<subpixel_accuracy)
                if mv_next_x_by_bx < -(search_range<<subpixel_accuracy):
                    mv_next_x_by_bx = -(search_range<<subpixel_accuracy)

        local_me_for_image(mv,ref,pred,block_size<<l,border_size>>l,blocks_in_y, blocks_in_x)
        
    pic_dwt_refPrev = pywt.wavedec2(pic_dwt_refPrev,TEXTURE_INTERPOLATION_FILTER,dwt_levels)
    pic_dwt_refNext = pywt.wavedec2(pic_dwt_refNext,TEXTURE_INTERPOLATION_FILTER,dwt_levels)
    pic_dwt_pred = pywt.wavedec2(pic_dwt_pred,TEXTURE_INTERPOLATION_FILTER,dwt_levels)

	
if __name__ == "__main__":

    #Define args parser and args
    parser = argparse.ArgumentParser(description='Block-based time-domain motion estimation.')
    parser.add_argument('-b', type=int, default=32,
                        help='block_size: Size of the blocks in the motion estimation process (Integer) (Default value: 32)')
    parser.add_argument('-d', type=int, default=0,
                        help='bordder_size: Size of the border of the blocks in the motion estimation process (Integer) (Default value: 0)')
    parser.add_argument('-e', type=str, default="even",
                        help='even_fn: Input file with the even pictures (String) (Default value: "even")')
    parser.add_argument('-i', type=str, default="imotion",
                        help='imotion_fn: Input file with the initial motion fields (String) (Default value: "imotion")')
    parser.add_argument('-m', type=str, default="motion",
                        help='motion_fn: Output file with the motion fields (String) (Default value: "motion")')
    parser.add_argument('-o', type=str, default="odd",
                        help='odd_fn: Input file with odd pictures (String) (Default value: "odd")')
    parser.add_argument('-p', type=int, default=9,
                        help='pictures: Number of images to process (Integer) (Default value: 9)')
    parser.add_argument('-x', type=int, default=352,
                        help='pixels_in_x: Size of the X dimension of the pictures (Integer) (Default value: 352)')
    parser.add_argument('-y', type=int, default=288,
                        help='pixels_in_y: Size of the Y dimension of the pictures (Integer) (Default value: 288)')
    parser.add_argument('-s', type=int, default=4,
                        help='search_range: Size of the searching area of the motion estimation (Integer) (Default value: 4)')
    parser.add_argument('-a', type=int, default=0,
                        help='subpixel_accuracy: Sub-pixel accuracy of the motion estimation (Integer) (Default value: 0)')

    #Parse args
    args = parser.parse_args()

    block_size = args.b
    border_size = args.d
    even_fn = args.e
    imotion_fn = args.i
    motion_fn = args.m
    odd_fn = args.o
    pictures = args.p
    pixels_in_x = args.x
    pixels_in_y = args.y
    search_range = args.s
    subpixel_accuracy = args.a

    #DO STUFF
	