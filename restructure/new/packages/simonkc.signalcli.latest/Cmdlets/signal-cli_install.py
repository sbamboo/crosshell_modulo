import os, subprocess, tarfile, shutil

path = os.path.abspath(os.path.join(os.path.dirname(CSScriptRoot),"..",".data","private"))

instFolder = os.path.join(path,"signal-cli")
downFile = os.path.join(path,"signal-cli-x.x.x.tar.gz")

try:
    fancyPants = csSession.exlibs.fancyPants
except AttributeError:
    fancyPants = csSession.cslib.piptools.fromPath(
        os.path.join(
            csSession.exlibs.__path__._path[0],
            "fancyPants.py"
        )
    )

if os.path.exists(instFolder):
    print("Signal-cli is already installed.")
else:
    if os.path.exists(downFile) != True:
        try:
            fancyPants.downloadFile_HandleGdriveVirWarn(
                url = "https://github.com/AsamK/signal-cli/releases/download/v0.13.3/signal-cli-0.13.3.tar.gz",
                filepath = downFile,
                handleGdriveVirWarn = False,
                loadingBar = True,
                title = f"Downloading {os.path.basename(downFile)}...",
                postDownText = "Done!"
            )
        except fancyPants.PostDownFileNotFound:
            if os.path.exists(downFile) == False:
                raise

    print("Unpacking archive...")
    try:
        # Open the tar.gz file
        with tarfile.open(downFile, "r:gz") as tar:
            # Extract its contents to the destination folder
            tar.extractall(path=instFolder)
        print(f"Successfully unpacked {os.path.basename(downFile)}.")
    except Exception as e:
        print(f"Error: {e}")

    print("Prepping...")
    newFolder = os.path.join(instFolder,os.listdir(instFolder)[0])
    contents = os.listdir(newFolder)
    # Move each file/directory to the parent folder
    for item in contents:
        item_path = os.path.join(newFolder, item)
        shutil.move(item_path, instFolder)

    print("Cleaning up...")
    os.rmdir(newFolder)
    os.remove(downFile)

    print("Done!")