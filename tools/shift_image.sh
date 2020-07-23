#!/usr/bin/env bash

i_image="/tmp/000.png"
o_image="/tmp/shifted000.png"
y_shift=1
x_shift=1

usage() {
    echo $0
    echo "Shift an image a number of pixels"
    echo "  [-i image to shift ($i_image)]"
    echo "  [-o image to create ($o_image)]"
    echo "  [-y number of pixels to shift in the vertical direction (the origin is the upper left corner) ($y_shift)]"
    echo "  [-x number of pixels to shift in the horizontal direction ($y_shift)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "i:o:y:x:?" opt; do
    case ${opt} in
        i)
            i_image="${OPTARG}"
            echo "input =" $i_image
            ;;
        o)
            o_image="${OPTARG}"
            echo "output =" $o_image
            ;;
        y)
            y_shift="${OPTARG}"
            echo "y_shift =" $y_shift
            ;;
        x)
            x_shift="${OPTARG}"
            echo "x_shift =" $x_shift
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

convert ${i_image} -roll ${x_shift}${y_shift} ${o_image}

set +x

