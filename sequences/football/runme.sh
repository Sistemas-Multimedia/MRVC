if test -f "football_422_ntsc.y4m"; then
    echo "$FILE exists."
else
    wget https://media.xiph.org/video/derf/y4m/football_422_ntsc.y4m
fi
ffmpeg -i football_422_ntsc.y4m -start_number 0 /tmp/football%03d.png
