import os
import sys
import inspect
from cslib import crshDebug

'''
Variables:
  CS_Args:          Contains the sys.argv arguments used to start crosshell, excluding the "currentscript"
  CS_Efile:         Contains the currently executing script from sys.argv
  CS_Startfile:     The file asigned as the startfile, using the internal argument "@startfile:<>"
  CS_PythonPath:    The path to the current python executable running python
  CS_Basedir:       The root directory of crosshell (not core)
  CS_CoreDir:       The /core directory of crosshell.
  CS_Pathtags:      The Pathtags added by crosshell.
  CS_PathtagMan:    ClassInstance of the pathtag manager.
  CS_Settings:      ClassInstance of the settings manager.
  CS_lp:            ClassInstance of the language provider.
  CS_Langpath:      Path of langfiles.
  CS_mPackFilePath: Path of mPackage files.
  CS_mPackPath:     Path of mPackages
  CS_PackageList:   The list of packages loaded into crosshell.

Variables/Settings:
  CS_CoreDir_RetrivalMode: How crosshell should retrive the coredir ("inspect" or "file"), default: "inspect"
  CS_SettingsFile:         The path to the settings file relative to the basedir
  crshDebug:               The default instance of the crosshell debugger
  CS_text:                 Instance of the crosshellGlobalTextSystem
  CS_DefSessionFile:       The default session file to load from relative to the basedir
  CS_PackagesFolder:       The folder to store packages in, relative to basedir
'''

# Settings
CS_CoreDir_RetrivalMode = "inspect"
CS_SettingsFile = f"{os.sep}assets{os.sep}settings.yaml"
CS_DefSessionFile = f"{os.sep}core{os.sep}default.session"
CS_PackagesFolder = f"{os.sep}packages"

# Handle mainfile argument
CS_Args = sys.argv
CS_Startfile = None
for arg in CS_Args:
    if "@startfile" in arg:
        CS_Startfile = (arg.split("@startfile:"))[-1]
if CS_Startfile is None:
    CS_Startfile = "Unknown"
# Handle some things
CS_Efile = CS_Args[0]
CS_Args.pop(0)
# Prep things from cslib
from cslib import *
CS_PythonPath = getExecutingPython()
# Get Directories
if CS_CoreDir_RetrivalMode.lower() == "inspect":
  CS_CoreDir = os.path.dirname( inspect.getabsfile(inspect.currentframe()) )
else:
  CS_CoreDir = os.path.abspath(os.path.dirname(__file__))
CS_BaseDir = os.path.abspath(os.path.join(CS_CoreDir,".."))

# Load pathtags (First instance)
from cslib._crosshellParsingEngine import pathtagManager
CS_Pathtags = {
   "CS_CoreDir": CS_CoreDir,
   "CS_BaseDir": CS_BaseDir
}
CS_PathtagMan = pathtagManager(CS_Pathtags)

# Create settings object
CS_Settings = modularSettingsLinker(f"{CS_BaseDir}{CS_SettingsFile}")
CS_Settings.createFile()
CS_Settings.addModule("crsh")

# Add language settings
CS_Settings.addProperty("crsh","Language.Default",{"1":"en-us"})
CS_Settings.addProperty("crsh","Language.DefaultList",f"{'{CS_BaseDir}'}{os.sep}core{os.sep}langlist.json")
CS_Settings.addProperty("crsh","Language.ListFormat","json")
CS_Settings.addProperty("crsh","Language.LangFormat","json")

# Add a debug settings and config the debugger
CS_Settings.addModule("crsh_debugger")
CS_Settings.addProperty("crsh_debugger", "Mode", "limited")
crshDebug.setDebugMode(CS_Settings.getProperty("crsh_debugger", "Mode"))

# Initate a formatter instance
from cslib._crosshellGlobalTextSystem import crosshellGlobalTextSystem
CS_text = crosshellGlobalTextSystem( pathtagInstance = CS_PathtagMan )
crshDebug.setFormatterInstance(CS_text) # Attatch the formatter to the Debugger

# Define a formattedPrint function using the formatter instance
def fprint(text):
  text = CS_text.parse(text)
  print(text)

# Create language path
CS_Langpath = pathObject([
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
  langPath=            CS_Langpath
)

# Populate language file
CS_lp.populateList()

# Create a session
csSession = crosshellSession(defaultSessionFile=f"{CS_BaseDir}{CS_DefSessionFile}")

# Create mPackageFile path
CS_mPackFilePath = pathObject([
  f"{CS_BaseDir}{CS_PackagesFolder}{os.sep}.files"
])

# Create mPackage path
CS_mPackPath = pathObject([
  f"{CS_BaseDir}{CS_PackagesFolder}"
])

# Load data from /packages
from cslib._crosshellMpackageSystem import loadPackages
CS_PackageList = loadPackages(CS_mPackFilePath,CS_mPackPath)