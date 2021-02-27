FILE=bus_cif.y4m
if test -f "$FILE"; then
    echo "$FILE exists."
else
    wget https://media.xiph.org/video/derf/y4m/bus_cif.y4m
fi
ffmpeg -i $FILE -start_number 0 /tmp/original_%03d.png
