''' MRVC/frame.py '''

import numpy as np
import cv2
import colored
if __debug__:
    import os
import matplotlib.pyplot as plt

def read(prefix:str, image_number:int) -> np.ndarray: # [row, column, component]
    #fn = name + ".png"
    fn = f"{prefix}{image_number:03d}.png"
    if __debug__:
        print(colored.fore.GREEN + f"image.read: {fn}", end=' ', flush=True)
    img = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    #try:
    #    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #except cv2.error:
    #    print(colored.fore.RED + f'image.read: Unable to read "{fn}"')
    #    raise
    #img = np.array(img, dtype=np.float32)
    if __debug__:
        print(img.shape, img.dtype, os.path.getsize(fn), colored.style.RESET)
    #return img.astype(np.int16)
    return img.astype(np.uint16)

def write(img:np.ndarray, prefix:str, image_number:int) -> None:
    _write(img, prefix, image_number)

def debug_write(img:np.ndarray, prefix:str, image_number:int) -> None:
    if __debug__:
        #_write(img.astype(np.uint16), name)
        _write(img, prefix, image_number)

def _write(img:np.ndarray, prefix:str, image_number:int) -> None:
    #fn = name + ".png"
    fn = f"{prefix}{image_number:03d}.png"
    #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(fn, img)
    if __debug__:
        print(colored.fore.GREEN + f"image.write: {fn}", img.shape, img.dtype, os.path.getsize(fn), colored.style.RESET)

def normalize(img: np.ndarray) -> np.ndarray: # [row, column, component]
    max_component = np.max(img)
    min_component = np.min(img)
    max_min_component = max_component - min_component
    return (img - min_component) / max_min_component

def get_image_shape(prefix:str) -> int:
    img = read(prefix, 0)
    return img.shape

def print_stats(image):
    for i in range(image.shape[2]):
        print("component", i, image[..., i].max(), image[..., i].min(), image[..., i].dtype)

def show_RGB_image(image, title=''):
    plt.figure(figsize=(16,16))
    plt.title(title, fontsize=20)
    plt.imshow(cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGR2RGB))
    print_stats(image)

def show_image(image, title=''):
    plt.figure(figsize=(16,16))
    plt.title(title, fontsize=20)
    plt.imshow(image)
    print_stats(image)

##########

def __read(name: str) -> np.ndarray: # [row, column, component]
    fn = name + ".png"
    img = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except cv2.error:
        print(colors.red(f'image.read: Unable to read "{fn}"'))
        raise
    #img = np.array(img, dtype=np.float32)
    if __debug__:
        print(f"image.read({name})", img.shape, img.dtype, os.path.getsize(fn))
    return img.astype(np.int16)

def __load(name: str) -> np.ndarray: # [component, row, column]
    fn = name + ".png"
    image = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    try:
        B,G,R = cv2.split(image)
    except ValueError:
        print(colors.red(f'image.load: Unable to read "{fn}"'))
        raise
    image = np.array([R, G, B], dtype=np.int16)
    if __debug__:
        print(f"image.load({name})", image.shape)
    return image

def __save(image: np.ndarray, name: str) -> None:
    fn = name + ".png"
    image = cv2.merge((image[0], image[1], image[2]))
    cv2.imwrite(fn, image)

def __debug_save(image: np.ndarray, name: str) -> None:
    if __debug__:
        save(image, name)
    
