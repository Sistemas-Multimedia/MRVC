import os
import sys

def AddSizes(path = "/tmp/", N = 5):
        tamanoTotal = 0.0
        tamanoTotalNuevo = 0.0 
        for i in range(N):            
            path_archivo_normal = os.path.join(path,"{:03d}".format(i)+".png")
            path_archivo_reducido = os.path.join(path,"LL{:03d}".format(i)+".png")
            tamanoTotalNuevo += os.stat(path_archivo_reducido).st_size
            path_archivo_reducido = os.path.join(path,"LH{:03d}".format(i)+".png")
            tamanoTotalNuevo += os.stat(path_archivo_reducido).st_size
            path_archivo_reducido = os.path.join(path,"HL{:03d}".format(i)+".png")
            tamanoTotalNuevo += os.stat(path_archivo_reducido).st_size
            path_archivo_reducido = os.path.join(path,"HH{:03d}".format(i)+".png")
            tamanoTotal += os.stat(path_archivo_normal).st_size
            tamanoTotalNuevo += os.stat(path_archivo_reducido).st_size
        print("Original " + str(tamanoTotal))
        print("Nuevo " + str(tamanoTotalNuevo))
        print("Ratio de compresion " + "{0:.5f}".format(tamanoTotal/tamanoTotalNuevo))

if __name__ =="__main__":
        if len(sys.argv) < 2:
             AddSizes()
        elif len(sys.argv) == 2:
            AddSizes(N=int(sys.argv[1]))            
        else:
            AddSizes(sys.argv[1],int(sys.argv[2]))
