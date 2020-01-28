#!/bin/bash
entrada=$1
salida=$2

suma_final=$(du /tmp/$salida | awk '{print $1}')
echo "El tamaño de las imagenes finales es $suma_final bytes"
suma_inicial=$(du /tmp/$entrada | awk '{print $1}')
echo "El tamaño de las imagenes iniciales es $suma_inicial bytes"
ratio=$(echo "scale=2; $suma_inicial/$suma_final" | bc)
echo "El ratio de compresion es $ratio"
