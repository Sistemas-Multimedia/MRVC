# Common stuff and routines

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def normalize(img):
    max_component = np.max(img)
    min_component = np.min(img)
    max_min_component = max_component - min_component
    return (img-min_component)/max_min_component

def load_img(prefix):
    img = cv2.imread(f"{prefix}.png", cv2.IMREAD_UNCHANGED)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.array(img)
    img = img.astype(np.float32) - 32768.0
    return img

def show_img(prefix):
    img = load_img(prefix)
    img = normalize(img)
    plt.figure(figsize=(10,10))
    plt.title(prefix, fontsize=20)
    plt.imshow(img)

def show_seq(prefix="/tmp/", frames=5):
    for i in range(frames):
        show_img(f"{prefix}{i:03d}")

def show_motion(prefix="/tmp/", frames=5):
    plt.figure(figsize=(10,10))
    prev = load_img(f"{prefix}000")
    imgplot = plt.imshow(normalize(prev))
    for i in range(1, frames, 1):
        img = load_img(f"{prefix}{i:03d}")
        diff = img - prev
        prev = img
        diff = normalize(diff)
        plt.figure(figsize=(10,10))
        plt.title(f"{prefix}{i:03d}", fontsize=20)
        plt.imshow(diff)
