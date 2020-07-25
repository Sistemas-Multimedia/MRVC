#!/usr/bin/env bash

output_seq_prefix="/tmp/moving_circle_"
image_width="256"
image_height="256"
diameter="30"
frames="10"
x_initial="80"
y_initial="40"

usage() {
    echo $0
    echo "Generate a moving circle from left to right"
    echo '  [-o prefix of the moving circle sequence ("'$output_seq_prefix'")]'
    echo "  [-h image height, number of pixels in the vertical direction ($image_width)]"
    echo "  [-w image width, number of pixels in the horizontal direction ($image_height)]"
    echo "  [-f frames, number of frames to generate ($frames)]"
    echo "  [-d circle diameter ($diameter)]"
    echo "  [-x initial X coordinate ($x_initial)]"
    echo "  [-y initial Y coordinate ($y_initial)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "o:h:w:f:d:y:x:?" opt; do
    case ${opt} in
        o)
            output_seq_prefix="${OPTARG}"
            echo "output =" $output_seq_prefix
            ;;
        h)
            image_height="${OPTARG}"
            echo "image_height =" $image_height
            ;;
        w)
            image_width="${OPTARG}"
            echo "image_width =" $image_width
            ;;
        f)
            frames="${OPTARG}"
            echo "frames =" $frames
            ;;
        d)
            diameter="${OPTARG}"
            echo "diameter =" $diameter
            ;;
        y)
            y_initial="${OPTARG}"
            echo "Initial Y coordinate =" $y_initial
            ;;
        x)
            x_initial="${OPTARG}"
            echo "Initial X coordinate =" $x_initial
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

i=0
while [ $i -le $((frames-1)) ]
do
    ii=$(printf "%03d" $i)
    convert -size ${image_width}x${image_height} xc:skyblue -fill white -stroke black -draw "circle $((x_initial+i)),$y_initial $((x_initial+diameter+i)),$y_initial" ${output_seq_prefix}${ii}.png
    i=$(( $i + 1 ))
done
