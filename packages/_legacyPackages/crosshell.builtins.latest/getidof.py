import os

try:
    path = csSession.registry["cmdlets"][argv[0]]["path"]

    path = path.replace(CS_PackDir,"")

    tem = CS_BaseDir + os.sep + "packages"

    path = path.replace(tem,"")

    path = path.replace(":.",":")

    path = path.strip(os.sep)

    pieces = path.split(os.sep)

    pieces[-1] = os.path.splitext(pieces[-1])[0]

    path = ""
    for i,piece in enumerate(pieces):
        if i == len(pieces)-1:
            path += ":" + piece
        else:
            path += "/" + piece

    if path.startswith("/"): path = path.replace("/","",1)

    print(path)
except:
    print(f"Cmdlet '{sargv}' not found!")