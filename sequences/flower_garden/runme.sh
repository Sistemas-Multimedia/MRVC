FILE=flower_garden_422_ntsc.y4m
if test -f "$FILE"; then
    echo "$FILE exists."
else
    wget https://media.xiph.org/video/derf/y4m/flower_garden_422_ntsc.y4m
fi
ffmpeg -i $FILE -start_number 0 /tmp/original_%03d.png
