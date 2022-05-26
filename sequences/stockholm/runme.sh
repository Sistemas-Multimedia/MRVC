#!/usr/bin/env bash

input_prefix="https://hpca.ual.es/~vruiz/videos/"
sequence="stockholm_1280x768x50x420x578.avi"
output_prefix="/tmp/original_"
number_of_frames=16

source ../extract_frames.sh -i $input_prefix -s $sequence -o $output_prefix -n $number_of_frames
