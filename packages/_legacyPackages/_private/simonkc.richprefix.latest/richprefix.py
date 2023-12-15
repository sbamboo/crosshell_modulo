import os
from cslib.externalLibs.netwa import simpleDownload,netwa
from cslib.externalLibs.filesys import pwshStyled as ps
import argparse

# [Arguments]
cparser = argparse.ArgumentParser(prog="richprefix",exit_on_error=False,add_help=False)
cparser.add_argument('-h', '--help', action='store_true', default=False, help='Shows help menu.')
cparser.add_argument('--exhelp', action='store_true', default=False, help='Shows help then exits.')
# Arguments
cparser.add_argument('-l','-load', dest="load", help="Preset to load")
cparser.add_argument('--debug', dest="debug", action='store_true', help="Debug")
# Options (Comsume al remaining arguments)
cparser.add_argument('options', nargs='*')
# Create main arguments object
try: argus = cparser.parse_args(argv)
except: argus = cparser.parse_args()
if argus.help or argus.exhelp:
    cparser.print_help()


# get presets
if os.path.exists(f"{CSScriptRoot}\presets.list") == True:
    presents_content_local = ps.getContent(f"{CSScriptRoot}\presets.list")

hasConn = netwa.has_connection()

if hasConn == False:
    presets_content = presents_content_local
else:
    presets_content_online = simpleDownload("https://raw.githubusercontent.com/simonkalmiclaesson/packagehand_repository/main/repository/cmdlet/_private/private_richprefix/presets.list","")
    if "# format" in (presets_content_online.decode()).split("\n")[0]:
        presets_content = (presets_content_online.decode()).split("\n")
    else:
        presets_content = (presets_content_online.decode()).split("\n")

#richprefix = cs_persistance("get","cs_prefix",cs_persistanceFile)
richprefix = csSession.data["per"].getProperty("crsh","Prefix")

try:
    load = int(argus.load)
except:
    exit()

if load != "" and load != None and load != int():
    if load != "0":
        if load > (len(presets_content)-1):
            #print(pt_format(cs_palette,f"\033[31mNo preset with index '{load}'\033[0m"))
            fprint("{f.red}No preset with index '" + str(load) + "'{r}")
        else:
            richprefix = presets_content[load]

    if argus.debug == True:
        #print(pt_format(cs_palette,f"\033[32m{richprefix}\033[0m"))
        print("{!32m}//"+str(richprefix)+"//{r}")
    if load <= (len(presets_content)-1):

        #Apply prefix
        csshell_prefix = richprefix.strip("'")
        #cs_persistance("set","cs_prefix",cs_persistanceFile,csshell_prefix)
        csSession.data["per"].chnProperty("crsh","Prefix",csshell_prefix)
    
