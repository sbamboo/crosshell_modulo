# [Imports]
import os
from cslib.externalLibs.conUtils import GetPlatform
from cslib import getPrefix,evalDynPrefix,autopipImport,getProfileFileContent
from cslib._crosshellGlobalTextSystem import parsePrefixDirTag
from cslib._crosshellParsingEngine import exclude_nonToFormat,include_nonToFormat
yaml = autopipImport("yaml","pyaml")

# [Functions]
def formatPrefix(csSession,prefix,curdir,dirEnabled,stdPrefix):
    return csSession.data["txt"].parse(parsePrefixDirTag(prefix,curdir,dirEnabled,stdPrefix))

# [Setup]
## Get version info from session
raw_data = csSession.data["ver"]

## Get platform
platformName = GetPlatform()
if platformName == None: platformName = "Unknown"

## Get persistance
persistance = csSession.data["per"]._getContent().copy()
## Get defaults from settings
defPrefix = csSession.data["set"].getProperty("crsh","Console.DefPrefix")
defEncoding = csSession.data["set"].getProperty("crsh","Formats.DefaultEncoding")
defTitle = csSession.data["set"].getProperty("crsh","Console.DefTitle")
settings = csSession.data['set']._getContent()
try:
    settings["crsh"]["Console"]["DefTitle"] = "//" + settings["crsh"]["Console"]["DefTitle"] + "//"
except: pass

## Get current prefix
current_prefix = evalDynPrefix(csSession,stdPrefix=defPrefix,encoding=defEncoding)
current_prefix_raw = "'//" + current_prefix + "//'"
current_prefix_ren = "'" + formatPrefix(csSession,current_prefix,csSession.data["dir"],False,defPrefix) + "'"
current_prefix_dir = "'" + formatPrefix(csSession,current_prefix,csSession.data["dir"],True,defPrefix) + "'"

try:
    if current_prefix != defPrefix:
        persistance["crsh"]["Prefix"] = "//" + current_prefix + "//"
except: pass

## Get current title
current_title = csSession.data["per"].getProperty("crsh","Title")
if current_title == None: current_title = defTitle

## Get commands
cmdlets = csSession.registry["cmdlets"]

## Get packages
packages = csSession.registry["packages"]

# [Functions]
def format_yaml(yamlstr=str,labelF=str,valueF=str) -> str:
    newstr = []
    for line in yamlstr.split("\n"):
        try:
            split = line.split(":")
            key = split[0]
            if len(line.split(":")) > 1:
                split.pop(0)
                value = ':'.join(split)
                line = f"{labelF}{key}:{valueF}{value}"
            else:
                line = f"{labelF}{key}{valueF}"
        except: pass
        newstr.append("  "+line)
    return '\n'.join(newstr)

def spaceString(string=str,space=" ") -> str:
    split = string.split("\n")
    for i,line in enumerate(split):
        split[i] = space + line
    return '\n'.join(split)

# [Prep settings]
headerFormat = "{!36m}"
labelFormat = "{!33m}"
sublabelFormat = "{!35m}"
valueFormat = "{!32m}"
resetFormat = "{!0m}"
errorFormat = "{!31m}"

# [Create block]
infoBlock = f'''
{'{!97m}{!44m}'}Shellinf cmdlet by Simon Kalmi Claesson, Version 1.0 (modulo){'{r}'}

{headerFormat}VersionInfo:
  {labelFormat}Name:      {valueFormat}{raw_data.get("name")}
  {labelFormat}Vernr:     {valueFormat}{raw_data.get("vernr")}
  {labelFormat}Tags:      {valueFormat}{raw_data.get("tags")}
  {labelFormat}Vid:       {valueFormat}{raw_data.get("vid")}
  {labelFormat}Channel:   {valueFormat}{raw_data.get("channel")}

{headerFormat}Console:
  {labelFormat}Basedir:   {valueFormat}{CS_BaseDir}
  {labelFormat}Coredir:   {valueFormat}{CS_CoreDir}
  {labelFormat}Assetsdir: {valueFormat}{CS_CoreDir}
  {labelFormat}Curdir:    {valueFormat}{CS_CurDir}
  
{headerFormat}PlatformInfo:
  {labelFormat}Platform: {valueFormat}{platformName}

{headerFormat}Arguments: {errorFormat}UNABLE TO LOAD!

{headerFormat}Title:
  {labelFormat}Title:    {valueFormat}{current_title}

{headerFormat}Prefix:
  {labelFormat}Current:  {valueFormat}{current_prefix_raw}
  {labelFormat}Rendered: {valueFormat}{current_prefix_ren}
  {labelFormat}Showdir:  {valueFormat}{current_prefix_dir}

{headerFormat}Profile:
  {labelFormat}MsgProfileFile: {valueFormat}{csSession.data["msp"]}
  {labelFormat}PyProfileFile:  {valueFormat}{csSession.data["pyp"]}
  {labelFormat}ProfileContent: {valueFormat}
{spaceString(getProfileFileContent(csSession),"    ")}

{headerFormat}Packages:
  {labelFormat}Legacy:   {valueFormat}{", ".join([os.path.basename(value) for value in packages["legacy"]])}
  {labelFormat}Modulo:   {valueFormat}{", ".join([os.path.basename(value) for value in packages["modulo"]])}

{headerFormat}Cmdlets/Pathables: {valueFormat}{", ".join([value for value in cmdlets])}

{headerFormat}Settings:
{format_yaml(yaml.dump(settings,sort_keys=False),labelFormat,valueFormat)}

{headerFormat}Persistance:
{format_yaml(yaml.dump(persistance,sort_keys=False),labelFormat,valueFormat)}
'''

# [Print]
#fprint(infoBlock)
#toformat,excludes = exclude_nonToFormat(infoBlock)
#formatted = csSession.data["txt"].parse(toformat)
#infoBlock = include_nonToFormat(formatted,excludes)
print(infoBlock)