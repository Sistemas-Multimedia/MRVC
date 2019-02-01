#rm -rf /tmp/stockholm

if [ -d /tmp/issues02 ]; then
    rm -rf /tmp/issues02
fi
    mkdir /tmp/issues02
 
    echo "mkdir"
if [ -d /tmp/mdwt ]; then
    rm -rf   /tmp/mdwt
    echo "mkdir mdwt"
fi
    mkdir /tmp/mdwt    
if [ -d /tmp/mcdwt ]; then
    rm -rf   /tmp/mcdwt
    echo "mkdir mcdwt"
fi
    mkdir /tmp/mcdwt
pathscript=$PWD
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
    filen=$( printf '%03d' $filex )
    echo $filen
    #mv $f $base
    mv $f $filen
done
cd $pathscript
#for f in /tmp/issues02/*; do
# ./DWT.py -i $f -d /tmp/000
#descomentar    ./DWT.py -i $f -d $f
#echo "./DWT.py -i $f -d /tmp/dwt"
#done

echo " transformada mdwt.py"
python -O ./MDWT.py -i /tmp/issues02/ -d /tmp/mdwt/  
# python -O 
echo " transformada ---"
echo python -O ./MCDWT.py -d /tmp/mdwt/ -m /tmp/mcdwt/  
 ls -al /tmp/mcdwt/ 
echo " transformada MCDWT.py"

