# Imports
import os
from cslib import autopipImport
#import webcolors
webcolors = autopipImport("webcolors")
xcolor = fromPath(f"{CSScriptRoot}{os.sep}xcolor.py")

sargv = xcolor.inputHandler(sargv)
ansStr = xcolor.autoToAnsiStr(sargv)
ansStr = xcolor.outputHandler(ansStr)
print(ansStr)