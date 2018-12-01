#!/usr/bin/env bash

sequence="/tmp/???_0_LL.png"

usage() {
    echo $0
    echo "Shows sequence of normalized images"
    echo "  [-i sequence to show ($sequence)]"
    echo "  [-? help]"
}

echo $0: parsing: $@

while getopts "i:?" opt; do
    case ${opt} in
        i)
            sequence="${OPTARG}"
            echo "input =" $sequence
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

echo $sequence

for image in $sequence;
do
    ./ycc2rgb.py -i $image -o /tmp/view_sequence.png
    convert -normalize /tmp/view_sequence.png ${image}.png
done

set +x
