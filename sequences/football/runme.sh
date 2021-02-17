FILE=football_422_ntsc.y4m
if test -f "$FILE"; then
    echo "$FILE exists."
else
    wget https://media.xiph.org/video/derf/y4m/football_422_ntsc.y4m #-P /tmp/
fi
ffmpeg -i $FILE -start_number 0 /tmp/football_%03d.png
