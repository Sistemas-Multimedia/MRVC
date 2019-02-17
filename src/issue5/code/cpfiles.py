from unipath import Path
from distutils.dir_util import copy_tree
#pip install unipath 

def cpfile():
    src="../../../sequences/stockholm"
    dst="../img"
    f = Path('../img/000.png')
    if (not f.exists()):
        copy_tree(src, dst)
        print("Archivos Copiados")
    else:
        print("Existe Archivo")