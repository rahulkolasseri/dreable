import os, sys, subprocess, shlex

from inspect import getsourcefile
from setup import setUp

from dotenv import load_dotenv

def run(command):
    subprocess.run(shlex.split(command))

def correctDir(move=False):
    pwd = os.path.dirname(getsourcefile(lambda:0))
    if pwd.lower() == os.getcwd().lower():
        return True
    elif move:
        print("moving to correct directory")
        os.chdir(pwd)
        return True
    else:
        print(pwd, os.getcwd())
        return False




########################################################################################

if __name__ == '__main__':

    correctDir(move=True)
    load_dotenv()
    
    setUp()
    correctDir(move=True)
    run("./venv/Scripts/Python.exe stablegram.py")


    sys.exit()



