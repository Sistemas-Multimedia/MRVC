''' MRVC/image_3.py
I/O routines for 3-component (color) images.
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

def read(prefix:str, image_number:int=0) -> np.ndarray: # [row, column, component]
    #fn = name + ".png"
    fn = f"{prefix}{image_number:03d}.png"
    #if __debug__:
    #    print(colored.fore.GREEN + f"image_3.read: {fn}", end=' ', flush=True)
    img = cv.imread(fn, cv.IMREAD_UNCHANGED)
    #print("--------", img.shape)
    #img = cv.imread(fn, cv.COLOR_BGR2RGB)
    #img = cv.imread(fn)
    try:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    except cv.error:
        print(colored.fore.RED + f'image_3.read: Unable to read "{fn}"')
        raise
    #print("=========", img.shape)
    #img = np.array(img, dtype=np.float32)
    #if __debug__:
    #    print(img.shape, img.dtype, os.path.getsize(fn), img.max(), img.min(), colored.style.RESET)
    logger.info(f"{fn} {img.shape} {img.dtype} {os.path.getsize(fn)} {img.max()} {img.min()}")
    #return img.astype(np.int16)
    #return img.astype(np.uint16)
    return img

def write(img:np.ndarray, prefix:str, image_number:int):
    #fn = name + ".png"
    fn = f"{prefix}{image_number:03d}.png"
    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
    cv.imwrite(fn, img, [cv.IMWRITE_PNG_COMPRESSION, _compression_level])
    command = f"optipng {fn}"
    logger.debug(command)
    subprocess.call(["bash", "-c", command])
    len_output = os.path.getsize(fn)
    #if __debug__:
    #    print(colored.fore.GREEN + f"image_3.write: {fn}", img.shape, img.dtype, len_output, img.max(), img.min(), colored.style.RESET)
    logger.info(f"{fn} {img.shape} {img.dtype} {len_output} {img.max()} {img.min()}")
    return len_output

def debug_write(img:np.ndarray, prefix:str, image_number:int):
    #fn = name + ".png"
    fn = f"{prefix}{image_number:03d}.png"
    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
    cv.imwrite(fn, img, [cv.IMWRITE_PNG_COMPRESSION, _compression_level])
    len_output = os.path.getsize(fn)
    #if __debug__:
    #    print(colored.fore.GREEN + f"image_3.write: {fn}", img.shape, img.dtype, len_output, img.max(), img.min(), colored.style.RESET)
    logger.info(f"{fn} {img.shape} {img.dtype} {len_output} {img.max()} {img.min()}")
    return len_output

def normalize(img: np.ndarray) -> np.ndarray: # [row, column, component]
    max_component = np.max(img)
    min_component = np.min(img)
    max_min_component = max_component - min_component
    return (img - min_component) / max_min_component

def get_shape(prefix:str) -> int:
    img = read(prefix, 0)
    return img.shape

def print_stats(image):
    for i in range(image.shape[2]):
        logger.info(f"component={i} max={image[..., i].max()} min={image[..., i].min()} avg={np.average(image[..., i])}")

def show(image, title='', size=(10, 10), fontsize=20):
    plt.figure(figsize=size)
    plt.title(title, fontsize=fontsize)
    #plt.imshow(cv.cvtColor(image.astype(np.uint8), cv.COLOR_BGR2RGB))
    plt.imshow(image)
    print_stats(image)

def show_normalized(image, title='', size=(10, 10), fontsize=20):
    plt.figure(figsize=size)
    plt.title(f"{title}\nmax={image.max()}\nmin={image.min()}\navg={np.average(image)}", fontsize=fontsize)
    #plt.imshow(cv.cvtColor(image.astype(np.uint8), cv.COLOR_BGR2RGB))
    image = normalize(image)
    plt.imshow(image)
    print_stats(image)

##########

def __read(name: str) -> np.ndarray: # [row, column, component]
    fn = name + ".png"
    img = cv.imread(fn, cv.IMREAD_UNCHANGED)
    try:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    except cv.error:
        print(colors.red(f'image.read: Unable to read "{fn}"'))
        raise
    #img = np.array(img, dtype=np.float32)
    if __debug__:
        print(f"image.read({name})", img.shape, img.dtype, os.path.getsize(fn))
    return img.astype(np.int16)

def __load(name: str) -> np.ndarray: # [component, row, column]
    fn = name + ".png"
    image = cv.imread(fn, cv.IMREAD_UNCHANGED)
    try:
        B,G,R = cv.split(image)
    except ValueError:
        print(colors.red(f'image.load: Unable to read "{fn}"'))
        raise
    image = np.array([R, G, B], dtype=np.int16)
    if __debug__:
        print(f"image.load({name})", image.shape)
    return image

def __save(image: np.ndarray, name: str) -> None:
    fn = name + ".png"
    image = cv.merge((image[0], image[1], image[2]))
    cv.imwrite(fn, image)

def __debug_save(image: np.ndarray, name: str) -> None:
    if __debug__:
        save(image, name)
    
