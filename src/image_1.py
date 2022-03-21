''' MRVC/image_1.py
I/O routines for 1-component (grayscale) images.
 '''

import numpy as np
import cv2 as cv
import colored
import os
import subprocess
import matplotlib.pyplot as plt

import logging
import logging_config
logger = logging.getLogger(__name__)
#logging.basicConfig(format="[%(filename)s:%(lineno)s %(levelname)s probando %(funcName)s()] %(message)s")
##logger.setLevel(logging.CRITICAL)
##logger.setLevel(logging.ERROR)
##logger.setLevel(logging.WARNING)
#logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

_compression_level = 9 # 0=min, 9=max

def read(prefix:str, image_number:int) -> np.ndarray: # [row, column, component]
    fn = f"{prefix}{image_number:03d}.png"
    #if __debug__:
        #print(colored.fore.GREEN + f"image_1.read: {fn}", end=' ', flush=True)
    img = cv.imread(fn, cv.IMREAD_UNCHANGED)
    logger.debug(f"{fn} {img.shape} {img.dtype} {os.path.getsize(fn)} {img.max()} {img.min()}")
    return img

def debug_write(img:np.ndarray, prefix:str, image_number:int=0):
    fn = f"{prefix}{image_number:03d}.png"
    cv.imwrite(fn, img, [cv.IMWRITE_PNG_COMPRESSION, _compression_level])
    len_output = os.path.getsize(fn)
    logger.info(f"image_1.write: {fn} {img.shape} {img.dtype} {len_output} {img.max()} {img.min()}")
    return len_output

def write(img:np.ndarray, prefix:str, image_number:int=0):
    fn = f"{prefix}{image_number:03d}.png"
    cv.imwrite(fn, img, [cv.IMWRITE_PNG_COMPRESSION, _compression_level])
    command = f"optipng {fn}"
    logger.debug(command)
    subprocess.call(["bash", "-c", command])
    len_output = os.path.getsize(fn)
    #if __debug__:
    #    print(colored.fore.GREEN + f"image_1.write: {fn}", img.shape, img.dtype, len_output, img.max(), img.min(), colored.style.RESET)
    logger.info(f"image_1.write: {fn} {img.shape} {img.dtype} {len_output} {img.max()} {img.min()}")
    return len_output

def normalize(img: np.ndarray) -> np.ndarray: # [row, column, component]
    max_component = np.max(img)
    min_component = np.min(img)
    max_min_component = max_component - min_component
    return (img - min_component) / max_min_component

def get_image_shape(prefix:str) -> int:
    img = read(prefix, 0)
    return img.shape

def print_stats(image):
    logger.info(f"max={image.max()} min={image.min()} avg={np.average(image)}")

def show(image, title='', size=(10, 10), fontsize=20):
    plt.figure(figsize=size)
    plt.title(title, fontsize=fontsize)
    plt.imshow(image, cmap='gray')
    print_stats(image)

def show_normalized(image, title='', size=(10, 10), fontsize=20):
    plt.figure(figsize=size)
    #plt.imshow(cv.cvtColor(image.astype(np.uint8), cv.COLOR_BGR2RGB))
    _max, _min, _avg = np.max(image), np.min(image), np.average(image)
    plt.title(f"{title} max={_max} min={_min} avg={_avg}", fontsize=fontsize)
    image = normalize(image)
    plt.imshow(image, cmap='gray')
    print_stats(image)

