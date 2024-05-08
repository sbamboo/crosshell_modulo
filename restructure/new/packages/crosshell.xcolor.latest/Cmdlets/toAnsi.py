# Imports
import os
autopipImport = csSession.cslib.piptools.autopipImport
fromPath = csSession.cslib.piptools.fromPath
#import webcolors
webcolors = autopipImport("webcolors")
xcolor = fromPath(f"{CSScriptRoot}{os.sep}xcolor.py",{"csSession":csSession})

sargv = xcolor.inputHandler(args.sargv)
ansStr = xcolor.autoToAnsiStr(sargv)
ansStr = xcolor.outputHandler(ansStr)
print(ansStr)