import os
import sys
import inspect

'''
Variables:
  CS_Args:            Contains the sys.argv arguments used to start crosshell, excluding the "currentscript"
  CS_Efile:           Contains the currently executing script from sys.argv
  CS_Startfile:       The file asigned as the startfile, using the internal argument "@startfile:<>"
  CS_PythonPath:      The path to the current python executable running python
  CS_Basedir:         The root directory of crosshell (not core)
  CS_CoreDir:         The /core directory of crosshell.
  CS_Pathtags:        The Pathtags added by crosshell.
  CS_PathtagMan:      ClassInstance of the pathtag manager.
  CS_Settings:        ClassInstance of the settings manager.
  CS_lp:              ClassInstance of the language provider.
  CS_LangpathObj:     Path of langfiles.
  CS_packFilePathObj: Path of package files.
  CS_packageList:     A dictionary of lists of packages, in format:   {"<packageType>":[list_of_paths_to_packages]}
  CS_Registry:        The main variable registry in crosshell.

Variables/Settings:
  CS_CoreDir_RetrivalMode: How crosshell should retrive the coredir ("inspect" or "file"), default: "inspect"
  CS_SettingsFile:         The path to the settings file relative to the basedir
  crshDebug:               The default instance of the crosshell debugger
  CS_Text:                 Instance of the crosshellGlobalTextSystem
  CS_DefSessionFile:       The default session file to load from relative to the basedir
  CS_PackagesFolder:       The folder to store packages in, relative to basedir
  CS_mPackPath:            Path of mPackages (the folder to install to)
  CS_lPackPath:            Path of lPackages/legacyPackages (the folder to install to)
'''

# [First things first]
# Enable ansi on windows
os.system("")

# [Imports from cslib]
from cslib import *
from cslib._crosshellParsingEngine import exclude_nonToFormat,include_nonToFormat
from cslib._crosshellParsingEngine import pathtagManager,crosshellParsingEngine
from cslib._crosshellGlobalTextSystem import crosshellGlobalTextSystem,standardHexPalette
from cslib._crosshellMpackageSystem import loadPackages,getPackageDataFromList
from cslib._crosshellModularityEngine import linkedFileModularise
from cslib.smartInput import sInputPrompt
from cslib.toad import toad
from cslib.datafiles import setKeyPath

# [Settings]
CS_ModuleReplacebleNames = ["console.py","inpparse.py","exec.py"]
CS_DefaultEncoding = "utf-8"
CS_CoreDir_RetrivalMode = "inspect"
CS_SettingsFile = f"{os.sep}assets{os.sep}settings.yaml"
CS_PersistanceFile = f"{os.sep}core{os.sep}persistance.yaml"
CS_DefSessionFile = f"{os.sep}core{os.sep}default.session"
CS_sInputHistoryFile = f"{os.sep}assets{os.sep}.history"
CS_PackagesFolder = f"{os.sep}packages"
CS_GlobalEntriesFile = f"{os.sep}globalEntries.json"
CS_VersionFile = f"{os.sep}version.yaml"
CS_MsgProfileFile = f"{os.sep}assets{os.sep}profile.msg"
CS_PyProfileFile = f"{os.sep}assets{os.sep}profile.py"
CS_BuiltInReaders = {"PLATFORM_EXECUTABLE":f"{'{CS_CoreDir}'}{os.sep}readers{os.sep}platexecs.py"}


# [Setup]
# Handle mainfile argument
CS_Args = sys.argv
CS_Startfile = "Unknown"
for arg in CS_Args:
    if "@startfile" in arg:
        CS_Startfile = (arg.split("@startfile:"))[-1]

# Set efile and args
CS_Efile = CS_Args[0]
CS_Args.pop(0)

# Prep things from cslib
CS_PythonPath = getExecutingPython()

# Get Directories
if CS_CoreDir_RetrivalMode.lower() == "inspect":
  CS_CoreDir = os.path.dirname( inspect.getabsfile(inspect.currentframe()) )
else:
  CS_CoreDir = os.path.abspath(os.path.dirname(__file__))
CS_BaseDir = os.path.abspath(os.path.join(CS_CoreDir,".."))
CS_AssetDir = f"{CS_BaseDir}{os.sep}assets"

# Apply presetting to moduleReplaceables
CS_ModuleReplacebles = {}
for repl in CS_ModuleReplacebleNames:
  CS_ModuleReplacebles[repl] = {"path":f"{CS_CoreDir}{os.sep}modules{os.sep}{repl}","obj":None}

# Fix subdirectories/paths
CS_mPackPath = f"{CS_BaseDir}{CS_PackagesFolder}"
CS_lPackPath = f"{CS_BaseDir}{CS_PackagesFolder}{os.sep}_legacyPackages"

# Load pathtags (First instance)
CS_Pathtags = {
   "CS_CoreDir": CS_CoreDir,
   "CS_BaseDir": CS_BaseDir,
   "CS_Packages": CS_PackagesFolder,
   "CS_mPackPath": CS_mPackPath,
   "CS_lPackPath": CS_lPackPath,
   "CS_AssetDir": CS_AssetDir
}
CS_PathtagMan = pathtagManager(CS_Pathtags)
CS_PathtagMan.ensureAl()

# Create settings object
CS_Settings = modularSettingsLinker(f"{CS_BaseDir}{CS_SettingsFile}",encoding=CS_DefaultEncoding,ensure=True)
CS_Settings.createFile()

# Create Persistance object
CS_Persistance = modularSettingsLinker(f"{CS_BaseDir}{CS_PersistanceFile}",encoding=CS_DefaultEncoding,ensure=True)
CS_Persistance.addModule("crsh")

# Add settings main module
CS_Settings.addModule("crsh")

# Setup first settings
CS_Settings.addProperty("crsh","Console.VerboseStart", True)
CS_Settings.addProperty("crsh","Console.StripAnsi", False)
from cslib.progressMsg import startupMessagingWProgress
st = startupMessagingWProgress(CS_Settings.getProperty("crsh","Console.VerboseStart"),CS_Settings.getProperty("crsh","Console.StripAnsi"),crshDebug,pgMax=30,pgIncr=3)

# VERBOSE START #
st.verb("Loading settings...")

# Add settings
## get data
_set = CS_Settings.getModule("crsh")
_set = setKeyPath(_set,"Console.DefPrefix","> ")
_set = setKeyPath(_set,"Console.DefTitle","Crosshell Modulo")
_set = setKeyPath(_set,"Console.PrefixEnabled",True)
_set = setKeyPath(_set,"Console.PrefixShowDir",True)
_set = setKeyPath(_set,"Console.DynamicPrefixes",True)
_set = setKeyPath(_set,"Console.RestrictDynPrefixes", False)
_set = setKeyPath(_set,"Console.FormatOutMode", "format")
_set = setKeyPath(_set,"Console.ClearOnStart", True)
_set = setKeyPath(_set,"Console.Welcome.ShowOnStart", True)
_set = setKeyPath(_set,"Console.Welcome.ShowVersionNotice", True)
_set = setKeyPath(_set,"Console.Welcome.ShowProfile", True)
_set = setKeyPath(_set,"Execution.HandleCmdletError", True)
_set = setKeyPath(_set,"Execution.PrintCmdletDebug", False)
_set = setKeyPath(_set,"Execution.SplitByNewline", True)
_set = setKeyPath(_set,"Execution.SafelyHandleExit",True)
_set = setKeyPath(_set,"Execution.OnlyAllowCmdlets",False)
_set = setKeyPath(_set,"Execution.PrintComments",True)
_set = setKeyPath(_set,"Parse.Text.Webcolors", True)
_set = setKeyPath(_set,"Formats.DefaultEncoding",CS_DefaultEncoding)
CS_Settings.encoding = CS_Settings.getProperty("crsh", "Formats.DefaultEncoding")
_set = setKeyPath(_set,"Language.Loaded",{"1":"en-us"})
_set = setKeyPath(_set,"Language._choices",[])
_set = setKeyPath(_set,"Language.DefaultList",f"{'{CS_BaseDir}'}{os.sep}assets{os.sep}langlist.json")
_set = setKeyPath(_set,"Language.ListFormat","json")
_set = setKeyPath(_set,"Language.LangFormat","json")
_set = setKeyPath(_set,"Language.LoadSameSuffixedLangs",True)
_set = setKeyPath(_set,"SmartInput.Enabled",True)
_set = setKeyPath(_set,"SmartInput.TabComplete",True)
_set = setKeyPath(_set,"SmartInput.History",True)
_set = setKeyPath(_set,"SmartInput.Highlight",True)
_set = setKeyPath(_set,"SmartInput.ShowToolbar",True)
_set = setKeyPath(_set,"SmartInput.MultiLine",False)
_set = setKeyPath(_set,"SmartInput.MouseSupport",True)
_set = setKeyPath(_set,"SmartInput.LineWrap",True)
_set = setKeyPath(_set,"SmartInput.CursorChar","BLINKING_BEAM")
_set = setKeyPath(_set,"SmartInput.Completions.IncludeStandards",True)
_set = setKeyPath(_set,"SmartInput.Completions.IncludeArgs",True)
_set = setKeyPath(_set,"SmartInput.Completions.IncludeCmdCustoms",True)
_set = setKeyPath(_set,"SmartInput.Completions.HideByContext",False)
_set = setKeyPath(_set,"SmartInput.Completions.ColorAliases",False)
_set = setKeyPath(_set,"SmartInput.HistorySuggest",True)
_set = setKeyPath(_set,"SmartInput.HistoryType","File")
_set = setKeyPath(_set,"SmartInput.HistoryFile",f"{'{CS_BaseDir}'}{CS_sInputHistoryFile}")
_set = setKeyPath(_set,"SmartInput.Styling.Enabled",True)
_set = setKeyPath(_set,"SmartInput.Styling.Inject",True)
_set = setKeyPath(_set,"SmartInput.Styling.Options",{"bottom-toolbar":"ansigreen"})
_set = setKeyPath(_set,"SmartInput.Styling.Completions",{"cmd":"fg:green","arg":"fg:red","custom":"fg:blue"})
_set = setKeyPath(_set,"Version.VerFile", f"{'{CS_CoreDir}'}{CS_VersionFile}")
_set = setKeyPath(_set,"Version.FileFormatVer", "1")
_set = setKeyPath(_set,"Packages.Options.LoadInFileHeader",False)
_set = setKeyPath(_set,"Packages.AllowedFileTypes.Cmdlets.INTERNAL_PYTHON",["py"])
_set = setKeyPath(_set,"Packages.AllowedFileTypes.Cmdlets.PLATFORM_EXECUTABLE",["win@exe","win@cmd","win@bat","lnx;mac@MIME_EXECUTABLE"])
_set = setKeyPath(_set,"Packages.AllowedFileTypes.Packages.Modulo",["mpackage","mpack","csmpack"])
_set = setKeyPath(_set,"Packages.AllowedFileTypes.Packages.Legacy",["package","pack","cspack"])
_set = setKeyPath(_set,"Packages.AllowedFileTypes.CmdletFiles.Conf", ["cfg","config","conf"])
_set = setKeyPath(_set,"Packages.AllowedFileTypes.CmdletFiles.Pack", ["json","cfg","conf","config"])
_set = setKeyPath(_set,"Packages.Readers.ReaderFile",f"{'{CS_BaseDir}'}{os.sep}assets{os.sep}readerfiles.json")
_set = setKeyPath(_set,"Packages.Formatting.Palettes.Selected",None)
_set = setKeyPath(_set,"Packages.Formatting.Palettes._choices",[])
_set = setKeyPath(_set,"Packages.Formatting.Mappings.Selected",None)
_set = setKeyPath(_set,"Packages.Formatting.Mappings._choices",[])
_set = setKeyPath(_set,"CGTS.ANSI_Hex_Palette",standardHexPalette)
_set = setKeyPath(_set,"CGTS.CustomMappings",{})
CS_Settings.set("crsh",_set)

# Default persistance
CS_Persistance.addProperty("crsh","Prefix",CS_Settings.getProperty("crsh","Console.DefPrefix"))
CS_Persistance.addProperty("crsh","Title",CS_Settings.getProperty("crsh","Console.DefTitle"))
CS_Persistance.addProperty("crsh","HasShownGuide",False)
CS_Persistance.addProperty("crsh","sInput.btoolbar_msg",None)

# Add function to quickly get encoding
def CS_GetEncoding():
  #global CS_Settings
  return CS_Settings.getProperty("crsh", "Formats.DefaultEncoding")

# Add a debug settings and config the debugger
CS_Settings.addModule("crsh_debugger")
CS_Settings.addProperty("crsh_debugger", "Scope", "error")
CS_Settings.addProperty("crsh_debugger","Execution.AllowRunAsInternal", True)

# Load debug mode from settings
crshDebug.setScope(CS_Settings.getProperty("crsh_debugger", "Scope"))

# VERBOSE START #
st.verb("Loading formatter...")

# Initate a formatter instance
palette = CS_Settings.getProperty("crsh","CGTS.ANSI_Hex_Palette")
customMappings = CS_Settings.getProperty("crsh","CGTS.CustomMappings")
CS_Text = crosshellGlobalTextSystem( pathtagInstance = CS_PathtagMan, palette=palette, parseWebcolor=CS_Settings.getProperty("crsh", "Parse.Text.Webcolors"), customTags=customMappings )
crshDebug.setFormatterInstance(CS_Text) # Attatch the formatter to the Debugger

# Set stripansi
CS_Text.stripAnsi = CS_Settings.getProperty("crsh","Console.StripAnsi")

# VERBOSE START #
st.verb("Does it work? {#DA70D6}*Toad*{r}")

# Define a formattedPrint function using the formatter instance
def fprint(text,end=None):
  toformat,excludes = exclude_nonToFormat(text)
  formatted = csSession.data["txt"].parse(toformat)
  text = include_nonToFormat(formatted,excludes)
  if end == None:
    print(text)
  else:
    print(text,end=end)

# VERBOSE START #
st.verb("Loading language provider...")

# Create language path
CS_LangpathObj = pathObject([
   f"{CS_CoreDir}{os.sep}lang",
   f"{CS_BaseDir}{os.sep}assets{os.sep}lang"
])

# Load language Provider
CS_lp = crosshellLanguageProvider(
  languageListFile =   CS_PathtagMan.eval(CS_Settings.getProperty("crsh","Language.DefaultList")),
  defaultLanguage =    CS_Settings.getProperty("crsh","Language.Loaded"),
  listFormat=          CS_Settings.getProperty("crsh","Language.ListFormat"),
  langFormat=          CS_Settings.getProperty("crsh","Language.LangFormat"),
  pathtagManInstance = CS_PathtagMan,
  langPath=            CS_LangpathObj,
  encoding=            CS_GetEncoding(),
  sameSuffixLoading=   CS_Settings.getProperty("crsh","Language.LoadSameSuffixedLangs")
)
crshDebug.setLanguageProvider(CS_lp) # Attach the language provider to the Debugger

# VERBOSE START #    not_translatable
st.verb(f"Populating languageList... (len: {len(CS_lp.languageList)})",l="cs.startup.populanglist._nonadrss_",ct={"len":len(CS_lp.languageList)})

# Populate language file
CS_lp.populateList()

# Add languagePrios to settings
CS_Settings.chnProperty("crsh","Language._choices",CS_lp.choices)

# Create a session
csSession = crosshellSession(defaultSessionFile=f"{CS_BaseDir}{CS_DefSessionFile}",encoding=CS_GetEncoding())


# [Handle Packages]
# Create packageFile pathobj, of where to get package-files from
CS_packFilePathObj = pathObject([
  f"{CS_BaseDir}{CS_PackagesFolder}{os.sep}.files"
])
for path in CS_packFilePathObj.get(): filesys.ensureDirPath(path) # Ensure al paths exists

# VERBOSE START #
st.verb("Loading packages...",l="cs.startup.loadpkgs")

# Retrive a list of packages in /packages and install those waiting for it, then add it to the packagesLabeledList
CS_packageList = {
  "modulo": loadPackages(
    findFilesPathObj=CS_packFilePathObj,
    DestinationPath=CS_mPackPath,
    packageExtensions=handleOSinExtensionsList(CS_Settings.getProperty("crsh","Packages.AllowedFileTypes.Packages.Modulo")),
    extraExclusions=[CS_lPackPath]
  ),
  "legacy": loadPackages(
    findFilesPathObj=CS_packFilePathObj,
    DestinationPath=CS_lPackPath,
    packageExtensions=handleOSinExtensionsList(CS_Settings.getProperty("crsh","Packages.AllowedFileTypes.Packages.Legacy"))
  )
}


# [Get version info]
CS_VersionData = crosshellVersionManager_getData(
  versionFile=   CS_PathtagMan.eval(CS_Settings.getProperty("crsh","Version.VerFile")),
  formatVersion= CS_Settings.getProperty("crsh","Version.FileFormatVer"),
  encoding=      CS_Settings.getProperty("crsh","Formats.DefaultEncoding")
)


# [Populate session]

# VERBOSE START #
st.verb(f"Populating session...",l="cs.startup.populatesession")

# Link
CS_Registry = csSession.registry
# Populate
CS_Registry["cmdlets"] = {}
csSession.data["set"] = CS_Settings
csSession.data["lng"] = CS_lp
csSession.data["par"] = crosshellParsingEngine
csSession.data["ptm"] = CS_PathtagMan
csSession.data["txt"] = CS_Text
csSession.data["per"] = CS_Persistance
csSession.data["cdr"] = CS_CoreDir
csSession.data["bdr"] = CS_BaseDir
csSession.data["adr"] = CS_AssetDir
csSession.data["gef"] = f"{CS_CoreDir}{CS_GlobalEntriesFile}"
csSession.data["ver"] = CS_VersionData
csSession.data["fpr"] = fprint
csSession.data["msp"] = f"{CS_BaseDir}{CS_MsgProfileFile}"
csSession.data["pyp"] = f"{CS_BaseDir}{CS_PyProfileFile}"
csSession.deb = crshDebug
CS_Registry["packages"] = CS_packageList
CS_Registry["packageData"] = getPackageDataFromList(CS_packageList,CS_DefaultEncoding)

# sinput thing
CS_Registry["toadInstance"] = toad(csSession)
if CS_Settings.getProperty("crsh","SmartInput.Enabled") == True:
  CS_Registry["sInputInstance"] = sInputPrompt(csSession)
  CS_Registry["toadInstance"].link_sInput(CS_Registry["sInputInstance"])
else:
  CS_Registry["sInputInstance"] = None


# [Setup Module Linkers]
# Create objs
for name in CS_ModuleReplacebles.keys():
  CS_ModuleReplacebles[name]["obj"] = linkedFileModularise(CS_ModuleReplacebles[name]["path"])
# Vars
CS_Console = CS_ModuleReplacebles["console.py"]["obj"]
CS_Inpparse = CS_ModuleReplacebles["inpparse.py"]["obj"]
CS_Exec = CS_ModuleReplacebles["exec.py"]["obj"]


# [Load package data]

# VERBOSE START #
st.verb(f"Loading readers...",l="cs.startup.loadreaders")

CS_Registry["dynPrefix"] = {}
# Find readerData
CS_Registry["readerData"] = toReaderFormat(
  dictFromSettings=CS_Settings.getProperty("crsh", "Packages.AllowedFileTypes.Cmdlets"),
  readerFile=CS_PathtagMan.eval(CS_Settings.getProperty("crsh", "Packages.Readers.ReaderFile")),
  encoding=CS_GetEncoding()
)
# Add builtins
for name,path in CS_BuiltInReaders.items():
  addReader(name, CS_PathtagMan.eval(path), CS_PathtagMan.eval(CS_Settings.getProperty("crsh", "Packages.Readers.ReaderFile")))

# Loader Function
def csLoadPackageData(packageList=dict,CS_Registry=dict):
  # cmdlets from modulo packages
  _mPackages = packageList.get("modulo")
  if _mPackages != None:
    from cslib.packageReaders.modulo import getDataFromList
    _data = getDataFromList(
      CS_Settings=CS_Settings,
      #modules
      CS_ModuleReplacebles=CS_ModuleReplacebles,
      #langpck
      langpck_provider=CS_lp,
      langpck_pathObj=CS_LangpathObj,
      #cmdlets
      cmdlets_confFileExts=CS_Settings.getProperty("crsh", "Packages.AllowedFileTypes.CmdletFiles.Conf"),
      cmdlets_rootFileExts=CS_Settings.getProperty("crsh", "Packages.AllowedFileTypes.CmdletFiles.Pack"),
      # others
      crshparentPath=CS_BaseDir,
      packages=_mPackages,
      registry=CS_Registry,
      encoding=CS_GetEncoding()
    )
    CS_Registry["cmdlets"] = _data["cmdlets"]
    CS_Registry["readerData"] = _data["readerData"]
  # cmdlets from legacyPackages
  _lPackages = packageList.get("legacy")
  if _lPackages != None:
    from cslib.packageReaders.legacy import getDataFromList
    CS_Registry["cmdlets"] = getDataFromList(
      settings=CS_Settings,
      crshparentPath=CS_BaseDir,
      packages=_lPackages,
      registry=CS_Registry,
      encoding=CS_GetEncoding(),
      confFileExts=CS_Settings.getProperty("crsh", "Packages.AllowedFileTypes.CmdletFiles.Conf"),
      rootFileExts=CS_Settings.getProperty("crsh", "Packages.AllowedFileTypes.CmdletFiles.Pack")
    )

# VERBOSE START #
amnt = len(CS_packageList.get("legacy")) + len(CS_packageList.get("modulo"))
st.verb("Loading package data... (Pkgs: {amnt})",l="cs.startup.loadpkgdata",ct={"amnt":amnt})

# Execute loaderFunction into registry
csLoadPackageData(CS_packageList,CS_Registry)

# VERBOSE START #
st.verb(f"Finishing up before console...",l="cs.startup.finishingup")

# [Update formatting choices]
try:
  palette_choices = list(CS_Registry["packFormatting"]["palettes"].keys())
except:
  palette_choices = []
CS_Settings.chnProperty("crsh","Packages.Formatting.Palettes._choices",palette_choices)

try:
  mapping_choices = list(CS_Registry["packFormatting"]["mappings"].keys())
except:
  mapping_choices = []
CS_Settings.chnProperty("crsh","Packages.Formatting.Mappings._choices",mapping_choices)

# [Apply formattings choices]
## get selected
selectedPalette = CS_Settings.getProperty("crsh","Packages.Formatting.Palettes.Selected")
selectedMapping = CS_Settings.getProperty("crsh","Packages.Formatting.Mappings.Selected")
## get data
selectedPalette_data = None
selectedMapping_data = None
if selectedPalette != None and selectedPalette != "":
  selectedPalette_data = CS_Registry["packFormatting"]["palettes"].get(selectedPalette)
if selectedMapping != None and selectedMapping != "":
  selectedMapping_data = CS_Registry["packFormatting"]["mappings"].get(selectedMapping)
## merge with settings
if selectedPalette_data != None:
  CS_Text.palette.update(selectedPalette_data)
if selectedMapping_data != None:
  CS_Text.customTags.update(selectedMapping_data)

# [Add possible languages to settings]
## Populate language file and re-evaluate sameSuffixes if enabled, this to get any package-loaded languages
if CS_Settings.getProperty("crsh","Language.LoadSameSuffixedLangs") == True:
  CS_lp.loadSameSuffixedLanguages()
  CS_lp.load()
  CS_Settings.chnProperty("crsh","Language.Loaded", CS_lp.languagePrios)

# [Setup cmdlet variable manager and link to registry]
CS_CmdletVarMan = CmdletVarManager(CS_Persistance)
csSession.data["cvm"] = CS_CmdletVarMan

# [Setup builtin variables]
CS_StdVars = {
  "True": True,
  "False": False,
  "Basedir": CS_BaseDir,
  "Coredir": CS_CoreDir
}
for key,value in CS_StdVars.items():
  CS_CmdletVarMan.setvar(key,value)

# [Execute console]
csSession.data["dir"] = CS_BaseDir

# Clear if was verbose-start
if CS_Settings.getProperty("crsh","Console.VerboseStart") == True:
    st.clr()

CS_Console.execute_internally(globals())