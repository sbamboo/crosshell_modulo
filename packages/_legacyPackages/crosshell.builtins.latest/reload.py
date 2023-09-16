# [CStags]
# restrictionMode = internal
# [TagEnd]

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

csLoadPackageData(CS_packageList,CS_Registry)