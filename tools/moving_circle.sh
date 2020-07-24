#!/usr/bin/env bash

output_seq_prefix="/tmp/moving_circle_"
image_width="256"
image_height="256"
circle_radius="30"
frames="10"

usage() {
    echo $0
    echo "Generate a moving circle from left to right"
    echo '  [-o prefix of the moving circle sequence ("'$output_seq_prefix'")]'
    echo "  [-h image height, number of pixels in the vertical direction ($image_width)]"
    echo "  [-w image width, number of pixels in the horizontal direction ($image_height)]"
    echo "  [-f frames, number of frames to generate ($frames)]"
    echo "  [-f circle radius ($circle_radius)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "o:h:w:f:r:?" opt; do
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
        r)
            circle_radius="${OPTARG}"
            echo "circle_radius =" $circle_radius
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
    convert -size ${image_width}x${image_height} xc:skyblue -fill white -stroke black -draw "circle $((42+i)),42 $((42+circle_radius+i)),42" ${output_seq_prefix}${ii}.png
    i=$(( $i + 1 ))
done
