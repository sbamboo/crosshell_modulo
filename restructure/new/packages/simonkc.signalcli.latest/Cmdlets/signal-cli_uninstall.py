import os, subprocess

path = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private","signal-cli"))

if os.path.exists(path):
    csSession.exlibs.filesys.filesys.deleteDirNE(path)
    print("Uninstalled signal-cli.")