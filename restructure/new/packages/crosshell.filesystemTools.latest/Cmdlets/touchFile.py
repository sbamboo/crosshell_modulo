import os
#from cslib.externalLibs.filesys import pwshStyled as ps
ps = csSession.filesys.pwshStyled

dirIn = ' '.join(args.argv)
dirIn.strip(" ")

if os.path.exists(dirIn) != True:
    ps.touchFile(dirIn,csSession.getEncoding())
    try:
        pass
    except:
        print(f"\033[31mError: Could not create file: '{dirIn}'\033[0m")
else:
    print(f"\033[31mError: File '{dirIn}' already exists.\033[0m")