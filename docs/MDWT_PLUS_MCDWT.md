# How to use MDWT_PLUS_MCDWT

First, you need a sequence of images from a video to transform using this script. 
After that, you can execute the script using the command: **python3 -O ./MDWT_PLUS_MCDWT.py -i ../sequences/stockholm/ -d /tmp/stockholm_ -N 5 -T 3 -K 2**

* **python3** is the version of python.
* **-i** is the image sequences path (in this example ../sequences/stockholm/).
* **-d** is the result path (in this example /tmp/stockholm_).
* **-N** is the number of images to transform.
* **-T** is the temporal level (number of times to execute the butterfly in the MCDWT transform).
* **-K** is the spatial level (number of times to execute the MDWT transform followed by the MCDWT transform).
