#!/usr/bin/env bash

input_prefix="https://media.xiph.org/video/derf/y4m/"
sequence="container_cif.y4m"
output_prefix="/tmp/original_"
number_of_frames=16


source ../extract_frames.sh -i $input_prefix -s $sequence -o $output_prefix -n $number_of_frames
