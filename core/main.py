import os
import sys
import inspect

'''
Variables:
  CS_Args:       Contains the sys.argv arguments used to start crosshell, excluding the "currentscript"
  CS_Efile:      Contains the currently executing script from sys.argv
  CS_Startfile:  The file asigned as the startfile, using the internal argument "@startfile:<>"
  CS_PythonPath: The path to the current python executable running python
  CS_Basedir:    The root directory of crosshell (not core)
  CS_CoreDir:    The /core directory of crosshell.
  CS_Pathtags:   The Pathtags added by crosshell.
  CS_PathtagMan: ClassInstance of the pathtag manager.
  CS_Settings:   ClassInstance of the settings manager.
  CS_lp:         ClassInstance of the language provider.

Variables/Settings:
  CS_CoreDir_RetrivalMode: How crosshell should retrive the coredir ("inspect" or "file"), default: "inspect"
  CS_SettingsFile:         The path to the settings file relative to the basedir
'''

# Settings
CS_CoreDir_RetrivalMode = "inspect"
CS_SettingsFile = f"{os.sep}assets{os.sep}settings.yaml"

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

# Create settings oject
CS_Settings = modularSettingsLinker(f"{CS_BaseDir}{CS_SettingsFile}")
CS_Settings.createFile()
CS_Settings.addModule("crsh")

# Add language settings
CS_Settings.addPropertie("crsh","Language.Default","en-us")
CS_Settings.addPropertie("crsh","Language.DefaultList",f"{'{CS_BaseDir}'}{os.sep}core{os.sep}langlist.json")
CS_Settings.addPropertie("crsh","Language.ListFormat","json")
CS_Settings.addPropertie("crsh","Language.LangFormat","json")

# Create language path
CS_Langpath = pathObject([
   f"{CS_CoreDir}{os.sep}lang",
   f"{CS_BaseDir}{os.sep}assets{os.sep}lang"
])

# Load language Provider
CS_lp = crosshellLanguageProvider(
  languageListFile =   CS_PathtagMan.eval(CS_Settings.getPropertie("crsh","Language.DefaultList")),
  defaultLanguage =    CS_Settings.getPropertie("crsh","Language.Default"),
  listFormat=          CS_Settings.getPropertie("crsh","Language.ListFormat"),
  langFormat=          CS_Settings.getPropertie("crsh","Language.LangFormat"),
  pathtagManInstance = CS_PathtagMan,
  langPath=            CS_Langpath
)

# Populate language file
CS_lp.populateList(keepExisting=True)