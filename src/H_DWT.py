# La parte de entrada/salida de este módulo está en
# desuso. Básicamente gestiona el desplazamiento de las componentes al
# rango de números naturales y obliga a usar 16 bits/componente,
# cuando esto en realidad depende del contexto.

''' MRVC/H.py

Provides:

1. DWT LH, HL and HH I/O.
2. H <-> {LH, HL, HH} transformation. '''

import numpy as np
import DWT
import cv2
import colored
if __debug__:
    import os
    import image_3 as image

def read(prefix: str, image_number: int, shape: tuple) -> tuple: # [LH, HL, HH], each one [rows, columns, components]
    ASCII_image_number = str(image_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    H = []
    sb = 0
    for sbn in subband_names:
        fn = f"{prefix}F{ASCII_image_number}{sbn}.png"
        if __debug__:
            print(colored.fore.GREEN + f"H.read({fn})", end=' ')
        subband = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
        #try:
        #    subband = cv2.cvtColor(subband, cv2.COLOR_BGR2RGB)
        #except cv2.error:
        #    print(colored.fore.RED + f'H.read: Unable to read "{fn}"')
        if __debug__:
            print(subband.shape, subband.dtype, os.path.getsize(fn), colored.style.RESET)
        subband_int32 = np.array(subband, dtype=np.int32)
        subband_int32 -= 32768
        padded_subband = np.zeros(shape)
        #rows_pad_width = (shape[0] - subband_int32.shape[0])//2
        #cols_pad_width = (shape[1] - subband_int32.shape[1])//2
        #print("padding with", rows_pad_width, cols_pad_width)
        #padded_subband[rows_pad_width:subband_int32.shape[0], cols_pad_width:subband_int32.shape[1]] = subband_int32
        pad = (shape[0] - subband_int32.shape[0], shape[1] - subband_int32.shape[1])
        print("padding with", pad)
        padded_subband[:subband_int32.shape[0], :subband_int32.shape[1], :] = subband_int32
        #padded_subband[subband_int32.shape[0]//2:subband]
        #if subband_int32.shape[0] != shape[0]:
        #    pad_width = (shape[0] - subband_int32.shape[0])//2
        #    subband_int32 = np.pad(subband_int32, (pad_width, 0, 0), 'constant', constant_values=(0, 0)) 
        #if subband_int32.shape[1] != shape[1]:
        #    pad_width = (shape[1] - subband_int32.shape[1])//2
        #    subband_int32 = np.pad(subband_int32, (0, pad_width, 0), 'constant', constant_values=(0, 0)) 
        H.append(padded_subband)
    return tuple(H)

def write(H: tuple, prefix: str, image_number: int) -> None:
    ASCII_image_number = str(image_number).zfill(3)
    if __debug__:
        print(colored.fore.GREEN + f"H_DWT.write({prefix}, {image_number})", end=' ')
    subband_names = ["LH", "HL", "HH"]
    sb = 0
    for sbn in subband_names:
        if __debug__:
            print(f"shape={H[sb].shape} max={H[sb].max()} min={H[sb].min()}", end=' ')
        subband = np.array(H[sb], dtype=np.int32)
        #subband = H[sb]
        #subband = H[i].astype(np.float32)
        subband += 32768
        assert (subband < 65536).all()
        assert (subband > -1).all()
        subband = subband.astype(np.uint16)
        #subband = cv2.cvtColor(subband, cv2.COLOR_RGB2BGR)
        fn = f"{prefix}F{ASCII_image_number}{sbn}.png"
        cv2.imwrite(fn, subband)
        sb += 1
        if __debug__:
            print(f"length={os.path.getsize(fn)}", end=' ')
    if __debug__:
        print(colored.style.RESET)

def interpolate(H: tuple) -> np.ndarray:
    LL = np.zeros(shape=(H[0].shape), dtype=np.float64)
    _H_ = DWT.synthesize_step(LL, H)
    return _H_

#if __debug__:
#    k = 0

def reduce(_H_: np.ndarray) -> tuple:
    _, H = DWT.analyze_step(_H_)
    if __debug__:
        global k
        unique, counts = np.unique(_, return_counts=True)
        print(f"H.reduce: unique={unique} counts={counts} ({len(counts)})")
        #image.debug_write(image.normalize(_).astype(np.uint8), f"/tmp/__{k:03d}")
        #k += 1
    return H

####################

def __read(fn:str, shape: tuple) -> tuple: # [LH, HL, HH], each one [rows, columns, components]
    fn = fn + ".png"
    resolution = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    ASCII_image_number = str(image_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    H = []
    sb = 0
    for sbn in subband_names:
        fn = f"{prefix}{sbn}{ASCII_image_number}.png"
        subband = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
        try:
            subband = cv2.cvtColor(subband, cv2.COLOR_BGR2RGB)
        except cv2.error:
            print(colors.red(f'H.read: Unable to read "{fn}"'))
        if __debug__:
            print(f"H.read({prefix}, {image_number})", subband.shape, subband.dtype, os.path.getsize(fn))
        subband_int32 = np.array(subband, dtype=np.int32)
        subband_int32 -= 32768
        padded_subband = np.zeros(shape)
        pad = (shape[0] - subband_int32.shape[0], shape[1] - subband_int32.shape[1])
        print("padding with", pad)
        padded_subband[:subband_int32.shape[0], :subband_int32.shape[1], :] = subband_int32
        H.append(padded_subband)
    return tuple(H)

