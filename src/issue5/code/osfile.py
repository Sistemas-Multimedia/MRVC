import os

def main():
    
    print("Current Working Directory 1:" , os.getcwd())
    
    
    try:
        # Change the current working Directory    
        os.chdir("../../")
        print("Directory changed")
    except OSError:
        print("Can't change the Current Working Directory")        

    print("Current Working Directory 2" , os.getcwd())
    
def img():
    print("Image directory", os.getcwd("./issue5/img"))
    
def pathlocal():
    print("Current Working Directory " , os.getcwd())
    
#if __name__ == '__main__':
#    main()