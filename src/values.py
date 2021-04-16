import numpy as np

def norm(x):
    max = x.max()
    min = x.min()
    return (x-min)/(max-min), max, min
    #return (frame.normalize(x)*255).astype(np.uint8)

def denorm(x, max, min):
    return x*(max-min)+min

def clip(x):
    return(np.clip(x+128, 0 ,255).astype(np.uint8))
