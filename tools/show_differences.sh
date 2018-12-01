#!/usr/bin/env bash

image1="/tmp/1.png"
image2="/tmp/2.png"
differences="/tmp/differences.png"

usage() {
    echo $0
    echo "Shows (as an normalized image) the differences between two images"
    echo "  [-1 input image one ($image1)]"
    echo "  [-2 input image two ($image2)]"
    echo "  [-o output difference image ($differences)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "1:2:o:?" opt; do
    case ${opt} in
        1)
            image1="${OPTARG}"
            echo "Image 1 =" $image1
            ;;
        2)
            image2="${OPTARG}"
	    echo "Image 2 =" $image2
            ;;
        o)
            differences="${OPTARG}"
	    echo "Difference image =" $differences
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

composite $image1 $image2 -compose difference tmp.png
convert tmp.png -auto-level $differences

set +x
