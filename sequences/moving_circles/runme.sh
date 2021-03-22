../../tools/moving_circle.sh -o /tmp/right -x 32 -y 16 -w 64 -h 32 -f 5 -d 10
../../tools/moving_circle.sh -o /tmp/left -x 32 -y 16 -w 64 -h 32 -f 5 -d 10 -a 0 -b -1
set -x
frames=5
i=0
while [ $i -le $((frames-1)) ]
do
    ii=$(printf "%03d" $i)
    convert -append /tmp/right${ii}.png /tmp/left${ii}.png ${ii}.png
    i=$(( $i + 1 ))
done
set -x
