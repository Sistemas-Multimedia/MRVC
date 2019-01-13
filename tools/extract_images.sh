wget http://www.hpca.ual.es/~vruiz/videos/stockholm_1280x768x50x420x578.avi
ffmpeg -i stockholm_1280x768x50x420x578.avi -vframes 7 %03d.png
