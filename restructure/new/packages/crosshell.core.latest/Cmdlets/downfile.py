import os

args:object
csSession:object

textsys = csSession.getregister("txt")

silent = False
overwrite = False
handleGdrive = False

if "--s" in args.argv:
    silent = True
    args.argv.remove("--s")

if "--f" in args.argv:
    overwrite = True
    args.argv.remove("--f")

if "--g" in args.argv:
    handleGdrive = True
    args.argv.remove("--g")

if len(args.argv) < 2:
    if silent == False: csSession.deb.perror("Invalid amount of arguments, give url and filepath!\nUse --s to hide this message.")
    exit()

url = args.argv[0]
path = args.argv[1]

if path.startswith("./"):
    path = os.path.join(os.getcwd(),path.replace("./","",1))

filepath = os.path.join(path,os.path.basename(url)).rstrip("\\")

if os.path.exists(filepath) and overwrite != True:
    if silent == False: csSession.deb.perror("{f.darkgray}"+f"Failed to download the file '{filepath}' since it already exists!\nUse --f to overwrite it or --s to hide this message."+"{r}")
    exit()


useLoadingBar = False
title = ""
postDownText = ""
gdriveWarnText = ""
if silent == False:
    useLoadingBar = True
    title = textsys.parse("{f.darkblue}Downloading "+os.path.basename(url)+"...{r}")
    postDownText = textsys.parse("{f.darkgreen}Done, downloaded file to "+os.path.basename(path)+"!{r}")
    gdriveWarnText = textsys.parse("{f.darkyellow}Found gdrive scan warning, attempting to extract link and download from there...{r}")
onFileExiError = "raise"
if overwrite == True:
    if silent == False:
        onFileExiError = "remove-with-warn"
    else:
        onFileExiError = "remove"

#Function to try and download a file, and if a gdrive-virus-scan-warning apprears try to extract the link and download it from there.
#    onFileExiError: "raise"/"ignore"/"ignore-with-warn"/"remove"/"remove-with-warn"
csSession.exlibs.fancyPants.downloadFile_HandleGdriveVirWarn(
    url = url,
    filepath = path,
    handleGdriveVirWarn = handleGdrive,
    loadingBar = useLoadingBar,
    title = title,
    postDownText = postDownText,
    handleGdriveVirWarnText = gdriveWarnText,
    raise_for_status = True,
    encoding = csSession.getEncoding(),
    onFileExiError = onFileExiError,
    yieldResp = False,
    stream = None
)