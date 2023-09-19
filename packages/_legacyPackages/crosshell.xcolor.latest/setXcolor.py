# Imports
import os
from cslib import autopipImport
#import webcolors
webcolors = autopipImport("webcolors")
xcolor = fromPath(f"{CSScriptRoot}{os.sep}xcolor.py")

lastArg = argv[-1]
lastArg = xcolor.inputHandler(lastArg)
_type = xcolor.getColorTypeStr(lastArg)
if _type != "str":
    hexStr = xcolor.autoToHexStr(lastArg)
    argv.pop(-1)
    argv[0] = "{" + hexStr + "}" + argv[0]
    print(' '.join(argv))
else:
    print(sargv)