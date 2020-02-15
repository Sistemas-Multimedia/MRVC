#!/usr/bin/env bash

width=1280
height=768

usage() {
    echo $0
    echo "Creates this sequence"
    echo "  [-w width ($width)]"
    echo "  [-h height ($height)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "w:h:?" opt; do
    case ${opt} in
        w)
            width="${OPTARG}"
            echo "width =" $width
            ;;
        h)
            height="${OPTARG}"
            echo "height =" $height
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

for i in {0..4}; do
    ii=$(printf "%03d" $i);
    bash ../../tools/create_black_image.sh -o $ii.png -w $width -h $height;
done

set +x

