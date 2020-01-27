cd /home/ubuntu/MCDWT/src

#!/bin/bash
clear
entrada=$1
salida=$2
url_video=$3
name_video=$4
limite=$5
T=$6

rm *.y4m

mkdir -p /tmp/$entrada
mkdir -p /tmp/$salida

rm /tmp/$entrada/*.*
rm /tmp/$salida/*.*

#Descargar archivo de video y extraer imagenes
wget $url_video
ffmpeg -i $name_video -vframes $limite /tmp/$entrada/%03d.png

d=0;
for i in /tmp/$entrada/0??.png; do 
  mv $i /tmp/$entrada/00$d.png; d=$((d+1));
done

#pasar MCDWT
python3 -O MDWT.py -p /tmp/$entrada/ 
python3 -O MCDWT.py -P 1 -p /tmp/$entrada/ -T $t

#copiar ficheros a salida
mv /tmp/$entrada/?????.png /tmp/$salida/

suma_final=$(du /tmp/$salida | awk '{print $1}')
echo "El tamaño de las imagenes finales es $suma_final bytes"
suma_inicial=$(du /tmp/$entrada | awk '{print $1}')
echo "El tamaño de las imagenes iniciales es $suma_inicial bytes"
ratio=$(echo "scale=2; $suma_inicial/$suma_final" | bc)
echo "El ratio de compresion es $ratio"
