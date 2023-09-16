import os
dirIn = ' '.join(argv)
dirIn.strip(" ")

old_dir = csSession.data["dir"]

if dirIn == "-":
    if os.path.exists("-") != True:
        dirIn = ".."

if os.path.exists(old_dir) != True:
    csSession.deb.perror("lng:cs.cmdlet.changedir.dirnotfound",{"dirIn":dirIn})
else:

    try:
        os.chdir(str(dirIn))
        csSession.data["dir"] = os.getcwd()
    except:
        csSession.deb.perror("lng:cs.cmdlet.changedir.dirnotfound",{"dirIn":dirIn})
        os.chdir(old_dir)