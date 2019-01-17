#!/usr/bin/env python3
from mcdwt import transform_step
import subprocess

# Test 1. Motion compensated H images should compress better (more)
# than intra H images.

# Test 2. Motion compensated H images should compress veeery well (much more than intra H images) when all images of the sequence are identical.

subprocess.call(["mkdir", "/tmp/eq"])
subprocess.call(["cp", "../images/000.png", "/tmp/eq/000.png"])
subprocess.call(["cp", "../images/000.png", "/tmp/eq/001.png"])
subprocess.call(["cp", "../images/000.png", "/tmp/eq/002.png"])
subprocess.call(["cp", "../images/000.png", "/tmp/eq/003.png"])
subprocess.call(["cp", "../images/000.png", "/tmp/eq/004.png"])
#import ipdb; ipdb.set_trace()
transform_step.forward('/tmp/eq/','/tmp/',5,1)
transform_step.backward('/tmp/','/tmp/res',5,1)

