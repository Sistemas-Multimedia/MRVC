FILE=park_joy_1080p50.y4m
if test -f "$FILE"; then
    echo "$FILE exists."
else
    (ulimit -f 112400; wget https://media.xiph.org/video/derf/y4m/park_joy_1080p50.y4m)
fi
ffmpeg -i $FILE -start_number 0 /tmp/original_%03d.png
