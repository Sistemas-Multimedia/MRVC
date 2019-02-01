#rm -rf /tmp/stockholm
pathscript=$PWD
if [ -d /tmp/issues02 ]; then
    rm -rf /tmp/issues02 
fi
    mkdir /tmp/issues02 
    echo "mkdir"
if [ -d /tmp/mdwt ]; then
    rm -rf   /tmp/mdwt 
    echo "mkdir dwt"
fi
    mkdir /tmp/mdwt

#wget http://www.hpca.ual.es/~vruiz/videos/stockholm_1280x768x50x420x578.avi --output-document=/tmp/stockholm.avi
wget http://www.hpca.ual.es/~vruiz/videos/flowergarden_352x288x30x420x250.avi --output-document=/tmp/stockholm.avi
ffmpeg -i /tmp/stockholm.avi -vframes 36 /tmp/issues02/%03d.png

cd /tmp/issues02/
for f in *.png; do
    echo $f
    base=${f%.*} 
    echo $base
    filex="$((10#$base-1))"
    echo $filex
    filen=$( printf '%03d' $filex )
    echo $filen
    #mv $f $base
    mv $f $filenx
done
<<<<<<< HEAD
cd $pathscript
for f in /tmp/issues02/*; do
    echo    python ./DWT.py -i $f -d   $f
done
echo " transformada MDWT.py"
echo python -O ./MDWT.py -i /tmp/issues02/ -d /tmp/mdwt/
echo " transformada MDWT.py"
=======
for f in /tmp/issues02/*; do
# ./DWT.py -i $f -d /tmp/000  
echo "./DWT.py -i $f -d $f"
#echo "./DWT.py -i $f -d /tmp/dwt"
done
>>>>>>> 5c59961440788c854864bd500f64055e423fad4e
#./add_32768_128.py /tmp/issues02/003.png /tmp/issues02/003_offset.png
#./sub_32768_128.py /tmp/issues02/003_offset.png /tmp/issues02/003_original.png
