#!/usr/bin/env bash

width=1280
height=768
n_frames=32
prefix=/tmp/black_

usage() {
    echo $0
    echo "Creates this sequence"
    echo "  [-w width ($width)]"
    echo "  [-h height ($height)]"
    echo "  [-n n_frames ($n_frames)]"
    echo "  [-p prefix ($prefix)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "w:h:n:p:?" opt; do
    case ${opt} in
        w)
            width="${OPTARG}"
            echo "width =" $width
            ;;
        h)
            height="${OPTARG}"
            echo "height =" $height
            ;;
        n)
            n_frames="${OPTARG}"
            echo "n_frames =" $n_frames
            ;;
        p)
            prefix="${OPTARG}"
            echo "prefix =" $prefix
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
#for i in {0..${n_frames}}; do
while [[ $i -le $n_frames ]]
do
    ii=$(printf "%03d" $i);
    bash ../../tools/create_black_image.sh -o $prefix$ii.png -w $width -h $height;
    ((i = i + 1))
done

set +x

