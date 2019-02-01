#!/usr/bin/env python
import subprocess
import sys
from sys import argv
from pathlib import Path

if len(sys.argv) == 2:
    fimg = sys.argv[1]
    #if (type(fimg) != int):
    #    fimg = 8
    print(fimg)
else:
    print("Error - Introduce los argumentos correctamente")
    print('Ejemplo: ./issue02.py  5')

 
scriptextr = './extraerimg.sh '+ fimg
 
subprocess.call(scriptextr, shell=True)

   
#subprocess.call("./DWT.py -i /tmp/issues02/0000 -d /tmp/issues02/0000", shell=True)
