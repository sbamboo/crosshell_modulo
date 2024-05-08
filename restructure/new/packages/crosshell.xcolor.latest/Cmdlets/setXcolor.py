# Imports
import os
autopipImport = csSession.cslib.piptools.autopipImport
fromPath = csSession.cslib.piptools.fromPath
#import webcolors
webcolors = autopipImport("webcolors")
xcolor = fromPath(f"{CSScriptRoot}{os.sep}xcolor.py",{"csSession":csSession})

lastArg = args.argv[-1]
lastArg = xcolor.inputHandler(lastArg)
_type = xcolor.getColorTypeStr(lastArg)
if _type != "str":
    hexStr = xcolor.autoToHexStr(lastArg)
    args.argv.pop(-1)
    args.argv[0] = "{" + hexStr + "}" + args.argv[0]
    print(' '.join(args.argv))
else:
    print(args.sargv)