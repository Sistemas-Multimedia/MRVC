import os
import sys

def RenameFiles(path = "/tmp/"):
    contador = 0
    for file in os.listdir(path):
        if file.endswith(".png"):
            oldName = os.path.join(path,file)
            numero = int(file[-8:][:-4])
            #anterior = numero - 1
            newName = os.path.join(path,"{:04d}".format(contador)+".png")
            os.rename(oldName,newName)
            contador = contador + 1

if __name__ =="__main__":
    if len(sys.argv) < 2:
        RenameFiles()
    else:
        RenameFiles(sys.argv[1])
