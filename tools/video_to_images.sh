rm -rf ../sequences/coastguard/*
#rm -rf /tmp/myVideo/myVideo
#wget http://www.hpca.ual.es/~vruiz/videos/stockholm_1280x768x50x420x578.avi --output-document=/tmp/myVideo.avi
ffmpeg  -i ../videos/coastguard.avi -vframes $1 -start_number 0 ../sequences/coastguard/coastguard_%03d.png
for i in ../sequences/coastguard/coastguard_*; do python3 ./add_32768_128.py  $i $i ;done;
for file in ../sequences/coastguard/*.png; do mv -- "$file" "${file%%.png}"; done;

