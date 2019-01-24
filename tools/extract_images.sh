#!/bin/env bash
wget http://www.hpca.ual.es/~vruiz/videos/un_heliostato.mp4
mkdir images
ffmpeg -i un_heliostato.mp4 -vframes 7 un_heliostato_%03d.png
mv *.png images
