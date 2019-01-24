rm -rf /tmp/stockholm
#wget http://www.hpca.ual.es/~vruiz/videos/stockholm_1280x768x50x420x578.avi --output-document=/tmp/stockholm.avi
ffmpeg -i /tmp/stockholm.avi -vframes 7 /tmp/%03d.png
./add_32768_128.py /tmp/003.png /tmp/003_offset.png
./sub_32768_128.py /tmp/003_offset.png /tmp/003_original.png
convert /tmp/003.png /tmp/003.ppm
convert /tmp/003_original.png /tmp/003_original.ppm
if cmp /tmp/003.ppm /tmp/003_original.ppm; then
    echo "Both files are identical :-)"
else
    echo "Files are different :-/"
fi
