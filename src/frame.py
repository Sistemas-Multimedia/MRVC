''' MRVC/frame.py '''

import numpy as np
import cv2
import colors
if __debug__:
    import os

def read(name: str) -> np.ndarray: # [row, column, component]
    fn = name + ".png"
    img = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except cv2.error:
        print(colors.red(f'frame.read: Unable to read "{fn}"'))
        raise
    #img = np.array(img, dtype=np.float32)
    if __debug__:
        print(f"frame.read({name})", img.shape, img.dtype, os.path.getsize(fn))
    return img.astype(np.int32)

def _write(img: np.ndarray, name: str) -> None:
    fn = name + ".png"
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(fn, img)
    if __debug__:
        print(f"frame.write({name})", img.shape, img.dtype, os.path.getsize(fn))

def write(img: np.ndarray, name: str) -> None:
    _write(img, name)

def debug_write(img: np.ndarray, name: str) -> None:
    if __debug__:
        _write(img.astype(np.uint16), name)

def normalize(img: np.ndarray) -> np.ndarray: # [row, column, component]
    max_component = np.max(img)
    min_component = np.min(img)
    max_min_component = max_component - min_component
    return (img - min_component) / max_min_component

##########

def load(name: str) -> np.ndarray: # [component, row, column]
    fn = name + ".png"
    frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    try:
        B,G,R = cv2.split(frame)
    except ValueError:
        print(colors.red(f'frame.load: Unable to read "{fn}"'))
        raise
    frame = np.array([R, G, B], dtype=np.int16)
    if __debug__:
        print(f"frame.load({name})", frame.shape)
    return frame

def save(frame: np.ndarray, name: str) -> None:
    fn = name + ".png"
    frame = cv2.merge((frame[0], frame[1], frame[2]))
    cv2.imwrite(fn, frame)

def debug_save(frame: np.ndarray, name: str) -> None:
    if __debug__:
        save(frame, name)
    
