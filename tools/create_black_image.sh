#!/usr/bin/env bash

image="/tmp/zero.png"
width=640
height=384

usage() {
    echo $0
    echo "Creates a zero (3 components, 8 bpp/component) image"
    echo "  [-i image to create ($image)]"
    echo "  [-w width ($width)]"
    echo "  [-h height ($height)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "i:w:h:?" opt; do
    case ${opt} in
        i)
            image="${OPTARG}"
            echo "input =" $image
            ;;
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

convert -size ${width}x${height} xc:black PNG24:${image}

set +x

