from cslib.externalLibs.filesys import filesys as fs
import os
if sargv != "" and sargv != None:
    if "." in sargv:
        sargv = os.path.abspath(os.path.join(csSession.data["dir"],sargv))
    fs.openFolder(sargv)
else:
    fs.openFolder(".")