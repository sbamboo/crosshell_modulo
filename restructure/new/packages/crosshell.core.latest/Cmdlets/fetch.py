import os

args:object
csSession:object

textsys = csSession.getregister("txt")

silent = False
handleGdrive = False
asByteString = False

if "--s" in args.argv:
    silent = True
    args.argv.remove("--s")

if "--g" in args.argv:
    handleGdrive = True
    args.argv.remove("--g")

if "--b" in args.argv:
    asByteString = True
    args.argv.remove("--b")

if len(args.argv) < 1:
    if silent == False: csSession.deb.perror("Invalid amount of arguments, give url!\nUse --s to hide this message.")
    exit()

url = args.argv[0]

useLoadingBar = False
title = ""
postDownText = ""
gdriveWarnText = ""
raiseForStatus = False
if silent == False:
    raiseForStatus = True
    useLoadingBar = True
    title = textsys.parse("{f.darkblue}Fetching "+os.path.basename(url)+"...{r}")
    gdriveWarnText = textsys.parse("{f.darkyellow}Found gdrive scan warning, attempting to extract link and download from there...{r}")
onFileExiError = "raise"

#Function to send a get request to a url, and if a gdrive-virus-scan-warning appears try to extract the link and send a get request to it instead.
resp = csSession.exlibs.fancyPants.getUrlContent_HandleGdriveVirWarn(
    url = url,
    handleGdriveVirWarn = handleGdrive,
    loadingBar = useLoadingBar,
    title = title,
    postDownText = "",
    handleGdriveVirWarnText = gdriveWarnText,
    raise_for_status=raiseForStatus,
    yieldResp=False
)

if asByteString == False:
    resp = resp.decode(csSession.getEncoding())

print(resp)