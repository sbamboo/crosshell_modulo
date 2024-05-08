import os
if args.sargv != "" and args.sargv != None:
    if "." in args.sargv:
        args.sargv = os.path.abspath(os.path.join(os.getcwd(),args.sargv))
    csSession.filesys.openFolder(args.sargv)
else:
    csSession.filesys.openFolder(".")