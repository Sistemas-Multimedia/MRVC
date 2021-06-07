''' MRVC/image_1.py
I/O routines for 1-component (grayscale) images.
 '''

import numpy as np
import cv2
import colored
if __debug__:
    import os
import matplotlib.pyplot as plt

def read(prefix:str, image_number:int) -> np.ndarray: # [row, column, component]
    fn = f"{prefix}{image_number:03d}.png"
    if __debug__:
        print(colored.fore.GREEN + f"image_1.read: {fn}", end=' ', flush=True)
    img = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    if __debug__:
        print(img.shape, img.dtype, os.path.getsize(fn), colored.style.RESET)
    return img

def write(img:np.ndarray, prefix:str, image_number:int) -> None:
        return _write(img, prefix, image_number)

def debug_write(img:np.ndarray, prefix:str, image_number:int) -> None:
    if __debug__:
        #_write(img.astype(np.uint16), name)
        return _write(img, prefix, image_number)

def _write(img:np.ndarray, prefix:str, image_number:int) -> None:
    fn = f"{prefix}{image_number:03d}.png"
    cv2.imwrite(fn, img)
    len_output = os.path.getsize(fn)
    if __debug__:
        print(colored.fore.GREEN + f"image_1.write: {fn}", img.shape, img.dtype, len_output, colored.style.RESET)
    return len_output

def normalize(img: np.ndarray) -> np.ndarray: # [row, column, component]
    max_component = np.max(img)
    min_component = np.min(img)
    max_min_component = max_component - min_component
    return (img - min_component) / max_min_component

def get_image_shape(prefix:str) -> int:
    img = read(prefix, 0)
    return img.shape

def print_stats(img):
    print(img.max(), img.min(), img.dtype)

def show(image, title='', size=(10, 10), fontsize=20):
    plt.figure(figsize=size)
    plt.title(title, fontsize=fontsize)
    plt.imshow(image)
    print_stats(image)
