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

    for i,piece in enumerate(pieces):
        if "." in piece:
            pieces[i] = piece.replace(".","_")

    path = ".".join(pieces)

    print(path)
except:
    print(f"Cmdlet '{sargv}' not found!")