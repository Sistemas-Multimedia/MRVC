#To use a download video
#rm -rf /tmp/myVideo/myVideo
#wget http://www.hpca.ual.es/~vruiz/videos/flowergarden_352x288x30x420x250.avi --output-document=/tmp/myVideo.avi
#ffmpeg  -i /tmp/myVideo.avi -vframes $1 -start_number 0 ../sequences/myVideo/myVideo_%03d.png

mkdir ../sequences/myVideo
rm -rf ../sequences/myVideo/* 
ffmpeg  -i $1 -vframes $2 -start_number 0 ../sequences/myVideo/%03d.png
#$1 = Video input path ,$2 = Images number 

for i in ../sequences/myVideo/*; do python3 ./add_offset.py -i $i -o $i ;done;
for file in ../sequences/myVideo/*.png; do mv -- "$file" "${file%%.png}"; done;