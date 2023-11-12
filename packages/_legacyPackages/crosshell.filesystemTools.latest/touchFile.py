import os
from cslib.externalLibs.filesys import pwshStyled as ps

dirIn = ' '.join(argv)
dirIn.strip(" ")

if os.path.exists(dirIn) != True:
    ps.touchFile(dirIn,CS_GetEncoding())
    try:
        pass
    except:
        print(f"\033[31mError: Could not create file: '{dirIn}'\033[0m")
else:
    print(f"\033[31mError: File '{dirIn}' already exists.\033[0m")