import os
dirIn = ' '.join(args.argv)
dirIn.strip(" ")

if os.path.exists(dirIn) == True:
    try:
        os.rmdir(dirIn)
    except:
        print(f"\033[31mError: Could not remove directory/file: '{dirIn}'\033[0m")
else:
    print(f"\033[31mError: Could not find directory/file: '{dirIn}'\033[0m")