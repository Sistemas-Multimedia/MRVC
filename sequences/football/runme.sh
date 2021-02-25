FILE=football_422_ntsc.y4m
if test -f "$FILE"; then
    echo "$FILE exists."
else
    wget https://media.xiph.org/video/derf/y4m/football_422_ntsc.y4m #-P /tmp/
fi
ffmpeg -i $FILE -vf "scale=720:488:force_original_aspect_ratio=decrease,pad=720:488:(ow-iw)/2:(oh-ih)/2,setsar=1" -start_number 0 /tmp/original_%03d.png
#ffmpeg -i $FILE -start_number 0 /tmp/football_%03d.png
