from cslib.externalLibs.conUtils import clear
from cslib import writeWelcome
from cslib.smartInput import sInputPrompt

CS_Registry["cmdlets"] = {}

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
csSession.registry["packages"] = CS_packageList
csLoadPackageData(CS_packageList,CS_Registry)

# [SmartInput]
_sInput_enabled = CS_Settings.getProperty("crsh","SmartInput.Enabled")
if _sInput_enabled == True:
  if CS_Registry["sInputInstance"] != None:
    CS_Registry["sInputInstance"]._updateSettings()
  else:
    CS_Registry["sInputInstance"] = sInputPrompt(csSession)
else:
  if CS_Registry["sInputInstance"] != None:
    CS_Registry["sInputInstance"] = None
# [Formatting]
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

if "--v" in argv or "/v" in argv or "--vis" in argv:
  clear()
  writeWelcome(csSession)