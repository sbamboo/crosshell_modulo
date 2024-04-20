import os, getpass

if csSession.exlibs.conUtils.IsWindows():
    userFolder = f"C:\\users\\{getpass.getuser()}\\"
else:
    userFolder = os.environ.get("HOME")

if not os.path.exists(userFolder):
    print("Failed, could not find user folder!")
else:
    localFolder = os.path.join(userFolder,".local")
    if not os.path.exists(localFolder):
        print(f"Failed, could not find the '~/.local' folder!")
    else:
        shareFolder = os.path.join(localFolder,"share")
        if not os.path.exists(shareFolder):
            print(f"Failed, could not find the '~/.local/share' folder!")
        else:
            usrDataFolder = os.path.join(shareFolder,"signal-cli")
            csSession.exlibs.filesys.filesys.deleteDirNE(usrDataFolder)
            print("Removed signal-cli userdata from '~/.local/share/signal-cli'.\n\n\033[31mRemember to remove the now-removed device from your other signal-devices!\033[0m")
