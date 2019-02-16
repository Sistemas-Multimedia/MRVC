#!/usr/bin/env bash

sequence="../sequences/stockholm/"
video="stockholm_1280x768x50x420x578.avi"
nframes=5
offset=32768

usage() {
    echo $0
    echo "Generate a sequence of images from a video"
    echo "  [-s sequence to generate ($sequence)]"
    echo "  [-v origin video ($video)]"
    echo "  [-n number of frames ($nframes)]"
    echo "  [-o offset ($offset)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "s:v:n:o:?" opt; do
    case ${opt} in
        s)
            sequence="${OPTARG}"
            echo "sequence =" $sequence
            ;;
        v)
            video="${OPTARG}"
            echo "video =" $video
            ;;
        n)
            nframes="${OPTARG}"
            echo "nframes =" $nframes
            ;;
        o)
            offset="${OPTARG}"
            echo "offset =" $offset
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

set -x

ffmpeg -i $video -vframes $nframes -start_number 0 /tmp/%03d.png

echo $frames

let i=0
while [ $i -lt $nframes ]
do
    _i_=$(printf "%03d" $i)
    python3 add_offset.py -i /tmp/$_i_.png -o $sequence$_i_.png -f $offset
    ((i++))
done

set +x
