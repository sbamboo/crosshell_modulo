import os
import sys
import inspect
from cslib import crshDebug

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

# [Imports from cslib]
from cslib import *
from cslib._crosshellParsingEngine import pathtagManager,crosshellParsingEngine
from cslib._crosshellGlobalTextSystem import crosshellGlobalTextSystem
from cslib._crosshellMpackageSystem import loadPackages
from cslib._crosshellModularityEngine import linkedFileModularise

# [Settings]
CS_ModuleReplacebleNames = ["console.py","inpparse.py","exec.py"]
CS_DefaultEncoding = "utf-8"
CS_CoreDir_RetrivalMode = "inspect"
CS_SettingsFile = f"{os.sep}assets{os.sep}settings.yaml"
CS_PersistanceFile = f"{os.sep}core{os.sep}persistance.yaml"
CS_DefSessionFile = f"{os.sep}core{os.sep}default.session"
CS_PackagesFolder = f"{os.sep}packages"
CS_BuiltInReaders = {"PLATFORM_EXECUTABLE":f"{'{CS_CoreDir}'}{os.sep}readers{os.sep}platexecs.py"}


# [Setup]
# Enable ansi on windows
os.system("")
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
   "CS_lPackPath": CS_lPackPath
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

# Add settings
CS_Settings.addProperty("crsh","Parse.Text.Webcolors", True)
CS_Settings.addProperty("crsh","Execution.HandleCmdletError", True)
CS_Settings.addProperty("crsh","Execution.PrintCmdletDebug", False)
CS_Settings.addProperty("crsh","Execution.SplitByNewline", True)
CS_Settings.addProperty("crsh","Execution.SafelyHandleExit",True)
CS_Settings.addProperty("crsh","Execution.OnlyAllowCmdlets",False)
CS_Settings.addProperty("crsh","Formats.DefaultEncoding",CS_DefaultEncoding)
CS_Settings.encoding = CS_Settings.getProperty("crsh", "Formats.DefaultEncoding")
CS_Settings.addProperty("crsh","Language.Default",{"1":"en-us"})
CS_Settings.addProperty("crsh","Language.DefaultList",f"{'{CS_BaseDir}'}{os.sep}assets{os.sep}langlist.json")
CS_Settings.addProperty("crsh","Language.ListFormat","json")
CS_Settings.addProperty("crsh","Language.LangFormat","json")
CS_Settings.addProperty("crsh","Packages.Options.LoadInFileHeader",False)
CS_Settings.addProperty("crsh","Packages.AllowedFileTypes.Cmdlets.INTERNAL_PYTHON",["py"])
CS_Settings.addProperty("crsh","Packages.AllowedFileTypes.Cmdlets.PLATFORM_EXECUTABLE",["win@exe","win@cmd","win@bat","lnx;mac@MIME_EXECUTABLE"])
CS_Settings.addProperty("crsh","Packages.AllowedFileTypes.Packages.Modulo",["mpackage","mpack","csmpack"])
CS_Settings.addProperty("crsh","Packages.AllowedFileTypes.Packages.Legacy",["package","pack","cspack"])
CS_Settings.addProperty("crsh","Packages.AllowedFileTypes.CmdletFiles.Conf", ["cfg","config","conf"])
CS_Settings.addProperty("crsh","Packages.AllowedFileTypes.CmdletFiles.Pack", ["json","cfg","conf","config"])
CS_Settings.addProperty("crsh","Packages.Readers.ReaderFile",f"{'{CS_BaseDir}'}{os.sep}assets{os.sep}readerfiles.json")
CS_Settings.addProperty("crsh","Console.DefPrefix","> ")
CS_Settings.addProperty("crsh","Console.DefTitle","Crosshell Modulo")
CS_Settings.addProperty("crsh","Console.PrefixEnabled",True)
CS_Settings.addProperty("crsh","Console.PrefixShowDir",True)

# Default persistance
CS_Persistance.addProperty("crsh","Prefix",CS_Settings.getProperty("crsh","Console.DefPrefix"))
CS_Persistance.addProperty("crsh","Title",CS_Settings.getProperty("crsh","Console.DefTitle"))

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

# Initate a formatter instance
CS_Text = crosshellGlobalTextSystem( pathtagInstance = CS_PathtagMan, parseWebcolor=CS_Settings.getProperty("crsh", "Parse.Text.Webcolors") )
crshDebug.setFormatterInstance(CS_Text) # Attatch the formatter to the Debugger

# Define a formattedPrint function using the formatter instance
def fprint(text):
  text = CS_Text.parse(text)
  print(text)

# Create language path
CS_LangpathObj = pathObject([
   f"{CS_CoreDir}{os.sep}lang",
   f"{CS_BaseDir}{os.sep}assets{os.sep}lang"
])

# Load language Provider
CS_lp = crosshellLanguageProvider(
  languageListFile =   CS_PathtagMan.eval(CS_Settings.getProperty("crsh","Language.DefaultList")),
  defaultLanguage =    CS_Settings.getProperty("crsh","Language.Default"),
  listFormat=          CS_Settings.getProperty("crsh","Language.ListFormat"),
  langFormat=          CS_Settings.getProperty("crsh","Language.LangFormat"),
  pathtagManInstance = CS_PathtagMan,
  langPath=            CS_LangpathObj,
  encoding=            CS_GetEncoding()
)
crshDebug.setLanguageProvider(CS_lp) # Attach the language provider to the Debugger

# Populate language file
CS_lp.populateList()

# Create a session
csSession = crosshellSession(defaultSessionFile=f"{CS_BaseDir}{CS_DefSessionFile}",encoding=CS_GetEncoding())


# [Handle Packages]
# Create packageFile pathobj, of where to get package-files from
CS_packFilePathObj = pathObject([
  f"{CS_BaseDir}{CS_PackagesFolder}{os.sep}.files"
])
for path in CS_packFilePathObj.get(): filesys.ensureDirPath(path) # Ensure al paths exists

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

# [Populate session]
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
csSession.deb = crshDebug

# [Setup Module Linkers]
# Create objs
for name in CS_ModuleReplacebles.keys():
  CS_ModuleReplacebles[name]["obj"] = linkedFileModularise(CS_ModuleReplacebles[name]["path"])
# Vars
CS_Console = CS_ModuleReplacebles["console.py"]["obj"]
CS_Inpparse = CS_ModuleReplacebles["inpparse.py"]["obj"]
CS_Exec = CS_ModuleReplacebles["exec.py"]["obj"]

# [Load package data]
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
# Execute loaderFunction into registry
csLoadPackageData(CS_packageList,CS_Registry)

# [Execute console]
csSession.data["dir"] = CS_BaseDir

CS_Console.execute_internally(globals())