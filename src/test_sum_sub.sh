rm -rf /tmp/stockholm
if [ -d /tmp/issues02 ]; then
    rm -rf /tmp/issues02 
fi
    mkdir /tmp/issues02 
    echo "mkdir"
if [ -d /tmp/dwt ]; then
    mkdir /tmp/issues02 
    echo "mkdir"
 fi


#wget http://www.hpca.ual.es/~vruiz/videos/stockholm_1280x768x50x420x578.avi --output-document=/tmp/stockholm.avi
wget http://www.hpca.ual.es/~vruiz/videos/flowergarden_352x288x30x420x250.avi --output-document=/tmp/stockholm.avi
ffmpeg -i /tmp/stockholm.avi -vframes $1 /tmp/issues02/%03d.png

cd /tmp/issues02/
for f in *.png; do
    #echo $f
    base=${f%.*} 
    #echo $base
    filex="$((10#$base-1))"
    #echo $filex
    filen=$( printf '%04d' $filex )
    echo $filen
    #mv $f $base
    mv $f $filen
done
#for f in /tmp/issues02/*; do
#./DWT.py -i $f -d /tmp/000  
#done
#./add_32768_128.py /tmp/issues02/003.png /tmp/issues02/003_offset.png
#./sub_32768_128.py /tmp/issues02/003_offset.png /tmp/issues02/003_original.png
