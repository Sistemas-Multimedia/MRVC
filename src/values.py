import numpy as np

def normalize(x):
    max = x.max()
    min = x.min()
    return (x-min)/(max-min), max, min
    #return (frame.normalize(x)*255).astype(np.uint8)

def denormalize(x, max, min):
    return x*(max-min)+min

def clip(x, low=0, high=255):
    #return(np.clip(x+128, low, high)#.astype(np.uint8))
    return(np.clip(x, low, high))#.astype(np.uint8))
