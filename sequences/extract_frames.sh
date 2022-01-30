#!/usr/bin/env bash

input_prefix="https://media.xiph.org/video/derf/y4m/"
sequence="container_cif.y4m"
#sequence=~/MRVC/sequences/akiyo_cif.y4m/runme.sh
output_prefix="/tmp/original_"
number_of_frames=16

usage() {
    #echo $0
    echo "Extracts the frames of a video sequence"
    echo "  [-i input prefix ($input_prefix)"
    echo "  [-s sequence file name ($sequence)"
    echo "  [-o output prefix ($output_prefix)]"
    echo "  [-n number of frames to extract ($number_of_frames)]"
    echo "  [-? help]"
}

#echo $0: parsing: $@

while getopts "i:s:o:n:?" opt; do
    case ${opt} in
        i)
            input_prefix="${OPTARG}"
            echo "input prefix =" $input_prefix
            ;;
        s)
            sequence="${OPTARG}"
            echo "sequence file name =" $sequence
            ;;
        o)
            output_prefix="${OPTARG}"
            echo "output prefix =" $output_refix
            ;;
        n)
            number_of_frames="${OPTARG}"
            echo "number of frames to extract =" $number_of_frames
            ;;
        ?)
            usage
            exit 0
            ;;
        \?)
            echo "Invalid option: -${OPTARG}" >&2
            usage
            exit 1
            ;;
        :)
            echo "Option -${OPTARG} requires an argument." >&2
            usage
            exit 1
            ;;
    esac
done

#source $sequence/runme.sh

if test -f "$sequence/$sequence"; then
    echo "$FILE exists. Only extracting ..."
else
    echo "Extracting ..."
    wget $input_prefix/$sequence --directory-prefix=~/MRVC/sequences/
fi

ffmpeg -i ~/MRVC/sequences/$sequence -start_number 0 -frames:v $number_of_frames ${output_prefix}%03d.png
