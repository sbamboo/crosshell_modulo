from cslib._crosshellGlobalTextSystem import parsePrefixDirTag

operation = str(argv[-1])
try:
    argv.pop(-1)
    prefix = argv[0:]
    # Handle prefix
    prefix = ' '.join(prefix)
    if prefix[0] == " ":
        prefix.replace(" ", "",1)
except:
    prefix = ""

# Handle decode
if "-decode" in operation:
    operation = operation.replace("-decode","")
    prefix = prefix.replace("{%1%}", "'")
    prefix = prefix.replace("{%2%}", '"')

prefix = prefix.replace("\\'","§")
prefix = prefix.replace("'","")
prefix = prefix.replace('§',"'")

def formatPrefix(csSession,prefix,curdir,dirEnabled,stdPrefix):
    return csSession.data["txt"].parse(parsePrefixDirTag(prefix,curdir,dirEnabled,stdPrefix))

# Set
if operation == "-set" or operation == "-s":
    csSession.data["per"].chnProperty("crsh","Prefix",prefix)
# Reset
if operation == "-reset" or operation == "-r":
    csSession.data["per"].chnProperty("crsh","Prefix",csSession.data["set"].getProperty("crsh","Console.DefPrefix"))
# Dir
if operation == "-dir":
    enabled = csSession.data["set"].getProperty("crsh","Console.PrefixShowDir")
    if enabled == "True" or enabled == True:
        enabled = False
    elif enabled == "False" or enabled == False:
        enabled = True
    csSession.data["set"].chnProperty("crsh","Console.PrefixShowDir",enabled)
# Enable
if operation == "-enable" or operation == "-e":
    csSession.data["set"].chnProperty("crsh","Console.PrefixEnabled",True)
# Disable
if operation == "-disable" or operation == "-d":
    csSession.data["set"].chnProperty("crsh","Console.PrefixEnabled",False)
# Get
if operation == "-get" or operation == "-g":
    pref = str(csSession.data["per"].getProperty("crsh","Prefix"))
    dirEnabled = csSession.data["set"].getProperty("crsh","Console.PrefixEnabled")
    stdPrefix = csSession.data["set"].getProperty("crsh","Console.DefPrefix")
    print("\033[36mCurrent Prefix:            \033[0m'//" + pref + "//'")
    print("\033[36mRendered prefix:           \033[0m'" + formatPrefix(csSession,prefix,csSession.data["dir"],dirEnabled,stdPrefix) + "'")
    print("\033[36mRendered prefix: \033[104m(Showdir)\033[0m \033[0m'" + formatPrefix(csSession,prefix,csSession.data["dir"],dirEnabled,stdPrefix) + "'")