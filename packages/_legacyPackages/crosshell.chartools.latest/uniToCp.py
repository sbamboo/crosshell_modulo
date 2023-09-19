
addZ = False

if "-z" in sargv:
    sargv = sargv.replace("-z","").strip(" ")
    addZ = True
if "--z" in sargv:
    sargv = sargv.replace("--z","").strip(" ")
    addZ = True

sargv = sargv.replace("u+","")
sargv = sargv.replace("U+","")

if len(sargv) == 6:
    out = sargv
elif len(sargv) == 9 or len(sargv) == 8:
    sargv = sargv.lstrip("{u.").rstrip("}")
    out = str(int(sargv, 16))
elif len(sargv) == 1:
    sargv = f"{ord(sargv):04X}"
    out = str(int(sargv, 16))
else:
    out = str(int(sargv, 16))

if addZ == True:
    out = "0" + out

print(out)