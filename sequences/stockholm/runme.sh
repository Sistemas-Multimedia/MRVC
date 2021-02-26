FILE=/tmp/stockholm_1280x768x50x420x578.avi
if test -f "$FILE"; then
    echo "$FILE exists."
else
    wget http://www.hpca.ual.es/~vruiz/videos/stockholm_1280x768x50x420x578.avi -P /tmp/
fi
ffmpeg -i $FILE -start_number 0 /tmp/original_%03d.png
