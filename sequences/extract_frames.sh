#!/usr/bin/env bash

URL="https://media.xiph.org/video/derf/y4m/"
sequence="container_cif.y4m"
#sequence=~/MRVC/sequences/akiyo_cif.y4m/runme.sh
output_prefix="/tmp/original_"
number_of_frames=16
first_frame=0

usage() {
    #echo $0
    echo "Extracts the frames of a video sequence"
    echo "  [-u URL ($URL)"
    echo "  [-s sequence file name ($sequence)"
    echo "  [-o output prefix ($output_prefix)]"
    echo "  [-n number of frames to extract ($number_of_frames)]"
    echo "  [-f first frame to extract ($first_frame)]"
    echo "  [-? help]"
}

#echo $0: parsing: $@

while getopts "u:s:o:n:f:?" opt; do
    case ${opt} in
        u)
            URL="${OPTARG}"
            echo "URL =" $URL
            ;;
        s)
            sequence="${OPTARG}"
            echo "sequence file name =" $sequence
            ;;
        o)
            output_prefix="${OPTARG}"
            echo "output prefix =" $output_prefix
            ;;
        n)
            number_of_frames="${OPTARG}"
            echo "number of frames to extract =" $number_of_frames
            ;;
        f)
            first_frame="${OPTARG}"
            echo "first frame to extract =" $first_frame
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

if test -f "$HOME/MRVC/sequences/$sequence"; then
    echo "$HOME/MRVC/sequences/$sequence exists. Only extracting ..."
else
    echo "Downloading ..."
    # (ulimit -f 112400; wget ...)
    wget $URL/$sequence --directory-prefix=$HOME/MRVC/sequences
fi
last_frame=$(echo $first_frame + $number_of_frames | bc)
ffmpeg -i $HOME/MRVC/sequences/$sequence -vf select="between(n\,"$first_frame"\,"$last_frame"),setpts=PTS-STARTPTS" -start_number $first_frame -frames:v $number_of_frames ${output_prefix}%03d.png
