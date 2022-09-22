import os, sys, subprocess, shlex


def run(command):
    subprocess.run(shlex.split(command))

def keyCheck():
    telegramToken = os.getenv("TELEGRAM_TOKEN")
    if telegramToken == None:
        return False
    return True



def setUp():
    cwd = os.getcwd()
    if os.path.exists(cwd + "/venv/"):
        print("venv exists")
    else:
        print("venv does not exist")
        print("Creating venv")
        run("python -m venv venv")
    
    print("Checking A1111NoUI submodule")
    run("git submodule update")

    print("Installing PTB requirements")
    run("./venv/Scripts/Python.exe -m pip install -r requirements.txt -q")

    if not keyCheck():
        print("Please set the environment variable TELEGRAM_TOKEN to your bot's token.")
        sys.exit()
    #subprocess.Popen(shlex.split("./venv/Scripts/Python.exe -m pip list"))
    print("Installing A111-NoUI requirements")
    os.chdir(cwd+"/A1111NoUI/")
    sys.path += [cwd+'/A1111NoUI']
    print (sys.path[-1])
    run("../venv/Scripts/Python.exe launch.py")