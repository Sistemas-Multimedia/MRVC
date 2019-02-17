import os
from os import scandir, getcwd
from os import listdir

def ls(donde,filext = '.png'):
    lstFiles = []
    os.chdir(donde)
    ruta = os.walk("./") 
    for root, dirs, files in ruta:
        for fichero in files:
            (nombreFichero, extension) = os.path.splitext(fichero)
            if(extension == filext):
                lstFiles.append(nombreFichero+extension)
    return lstFiles