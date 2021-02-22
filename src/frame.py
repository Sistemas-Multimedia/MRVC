''' MRVC/frame.py '''

import numpy as np
import cv2
import colors

def read(prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}{ASCII_frame_number}.png"
    frame = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    try:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except cv2.error:
        print(colors.red(f'frame.read: Unable to read "{fn}"'))
        raise
    frame = np.array(frame, dtype=np.float64)
    #print(frame.shape)
    return frame # [rows, columns, components]

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
    
def _write(frame, prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    fn = f"{prefix}{ASCII_frame_number}.png"
    print(frame.shape, fn)
    frame = frame.astype(np.uint8)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imwrite(fn, frame)

def debug_write(frame, prefix, frame_number):
    if __debug__:
        _write(frame, prefix, frame_number)

def write(frame, prefix, frame_number):
    _write(frame, prefix, frame_number)

def normalize(frame):
    max_component = np.max(frame)
    min_component = np.min(frame)
    max_min_component = max_component - min_component
    return (frame - min_component) / max_min_component
