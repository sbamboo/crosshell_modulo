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
  CS_text:                 Instance of the crosshellGlobalTextSystem
  CS_DefSessionFile:       The default session file to load from relative to the basedir
  CS_PackagesFolder:       The folder to store packages in, relative to basedir
  CS_mPackPath:            Path of mPackages (the folder to install to)
  CS_lPackPath:            Path of lPackages/legacyPackages (the folder to install to)
'''

# [Imports from cslib]
from cslib import *
from cslib._crosshellParsingEngine import pathtagManager
from cslib._crosshellGlobalTextSystem import crosshellGlobalTextSystem
from cslib._crosshellMpackageSystem import loadPackages

# [Settings]
CS_CoreDir_RetrivalMode = "inspect"
CS_SettingsFile = f"{os.sep}assets{os.sep}settings.yaml"
CS_DefSessionFile = f"{os.sep}core{os.sep}default.session"
CS_PackagesFolder = f"{os.sep}packages"


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

# Fix subdirectories/paths
CS_mPackPath = f"{CS_BaseDir}{CS_PackagesFolder}"
CS_lPackPath = f"{CS_BaseDir}{CS_PackagesFolder}{os.sep}.legacyPackages"

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
CS_Settings = modularSettingsLinker(f"{CS_BaseDir}{CS_SettingsFile}")
CS_Settings.createFile()

# Add settings main module
CS_Settings.addModule("crsh")

# Add language settings
CS_Settings.addProperty("crsh","Language.Default",{"1":"en-us"})
CS_Settings.addProperty("crsh","Language.DefaultList",f"{'{CS_BaseDir}'}{os.sep}core{os.sep}langlist.json")
CS_Settings.addProperty("crsh","Language.ListFormat","json")
CS_Settings.addProperty("crsh","Language.LangFormat","json")
CS_Settings.addProperty("crsh","Packages.AllowedFileTypes.Packages.Modulo",["mpackage","mpack","csmpack"])
CS_Settings.addProperty("crsh","Packages.AllowedFileTypes.Packages.Legacy",["package","pack","cspack"])
CS_Settings.addProperty("crsh","Packages.AllowedFileTypes.Cmdlets",[".py"])

# Add a debug settings and config the debugger
CS_Settings.addModule("crsh_debugger")
CS_Settings.addProperty("crsh_debugger", "Mode", "limited")

# Load debug mode from settings
crshDebug.setDebugMode(CS_Settings.getProperty("crsh_debugger", "Mode"))

# Initate a formatter instance
CS_text = crosshellGlobalTextSystem( pathtagInstance = CS_PathtagMan )
crshDebug.setFormatterInstance(CS_text) # Attatch the formatter to the Debugger

# Define a formattedPrint function using the formatter instance
def fprint(text):
  text = CS_text.parse(text)
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
  langPath=            CS_LangpathObj
)

# Populate language file
CS_lp.populateList()

# Create a session
csSession = crosshellSession(defaultSessionFile=f"{CS_BaseDir}{CS_DefSessionFile}")


# [Handle Packages]
# Create packageFile pathobj, of where to get package-files from
CS_packFilePathObj = pathObject([
  f"{CS_BaseDir}{CS_PackagesFolder}{os.sep}.files"
])
for path in CS_packFilePathObj.get(): filesys.ensureDirPath(path) # Ensure al paths exists

# Retrive a list of packages in /packages and install those waiting for it, then add it to the packagesLabeledList
CS_packageList = {
  "modulo": loadPackages(CS_packFilePathObj,CS_mPackPath,CS_Settings.getProperty("crsh","Packages.AllowedFileTypes.Packages.Modulo")),
  "legacy": loadPackages(CS_packFilePathObj,CS_lPackPath,CS_Settings.getProperty("crsh","Packages.AllowedFileTypes.Packages.Legacy"))
}

# [Populate session]
# Link
CS_Registry = csSession.registry
# Populate
CS_Registry["cmdlets"] = []
csSession.data["set"] = CS_Settings
csSession.data["lng"] = CS_lp

# [Load package data]
# Find readerData
CS_Registry["readerData"] = toReaderFormat(CS_Settings.getProperty("crsh", "Packages.AllowedFileTypes.Cmdlets"))
print(CS_Registry["readerData"])
# Loader Function
def csLoadPackageData(packageList=dict,CS_Registry=dict):
  # cmdlets from modulo packages
  _mPackages = packageList.get("modulo")
  if _mPackages != None:
    from cslib.packageReaders.modulo import getDataFromList
    CS_Registry = getDataFromList(_mPackages,CS_Registry)
  # cmdlets from legacyPackages
  _lPackages = packageList.get("legacy")
  if _lPackages != None:
    from cslib.packageReaders.legacy import getDataFromList
    CS_Registry = getDataFromList(_lPackages,CS_Registry)
# Execute loaderFunction into registry
csLoadPackageData(CS_packageList,CS_Registry)

# Registry or just path and then functions?
cmdlets = {
  "test": {
    "name": "test",
    "path": "..\\test.py",
    "fending": ".py",
    "aliases": ["test2"],
    "desc": "Testing some shi",
    "args": ["--do","-dont <smth>"],
    "blockCommonParameters": False,
    "encoding": "utf-8"
  }
}
'''Mass variable registry!'''



crshDebug.print("hi",onMode="on;limited")