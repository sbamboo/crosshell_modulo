'''
CSlib: CrosshellMpackageSystem contains crosshells code to handle modules.
'''

import os
from cslib.datafiles import _fileHandler
from cslib.externalLibs.filesys import filesys

def GetFilesByExt(path=str,extensions=list):
    """Cslib.CMPS: Retrives a list of files in a folder if the extension match a given list."""
    packageFiles = []
    objects = filesys.scantree(path)
    for object in objects:
        fending = filesys.getFileExtension(object.name)
        name = filesys.getFileName(object.name)
        if fending.lower() in extensions:
            packageFiles.append({name:object.path})
    return packageFiles

def listNonHiddenFolders(path, maxDepth=None, travelSymlink=False):
    """Cslib: Os walks a path with a maxdepth and returns each path to a folder where no path-component starts with ."""
    nonHiddenFolders = []
    for root, dirs, _ in os.walk(path, followlinks=travelSymlink):
        if maxDepth is not None and root.count(os.path.sep) - path.count(os.path.sep) >= maxDepth:
            continue
        for dirName in dirs:
            fullPath = os.path.join(root, dirName)
            if not any(part.startswith('.') for part in fullPath.split(os.path.sep)):
                nonHiddenFolders.append(fullPath)
    return nonHiddenFolders

def getFoldersInPath(path,handleSymlinks=False):
    """Cslib: Gets each folder in a path, also handles symlinks."""
    folders = []
    for item in os.listdir(path):
        itemPath = os.path.join(path, item)
        if os.path.islink(itemPath):  # Check if it's a symlink
            if handleSymlinks == True:
                targetPath = os.path.realpath(itemPath)  # Resolve symlink
                if os.path.isdir(targetPath):  # Check if the target is a directory
                    folders.append(targetPath)
        elif os.path.isdir(itemPath):  # Check if it's a directory
            folders.append(itemPath)
    return folders

def _getInstalledLegacyPackages(path=str, exclusionList=list, traverseDepth=None, travelSymlink=False):
    """Function to load legacy packages, this is however expensive since it will mark each folder that isn't "hidden"."""
    packages = []
    for subpath in listNonHiddenFolders(path, traverseDepth, travelSymlink):
        if subpath != path and subpath not in [*exclusionList,*packages]:
            packages.append(subpath)
    return packages

def _getNameOfModuloPackage(packageConfigFile=str,encoding="utf-8",fileIsStream=False):
    if fileIsStream == True:
        configFilepath = packageConfigFile.filepath
    else:
        configFilepath = packageConfigFile
    dataRaw = _fileHandler(filesys.getFileExtension(configFilepath),"get",packageConfigFile,encoding=encoding,fileIsStream=fileIsStream)
    name = os.path.basename(os.path.dirname(configFilepath))
    if dataRaw.get("package") != None:
        if dataRaw["package"].get("name") != None:
            name = dataRaw["package"]["name"]
        if dataRaw["package"].get("author") != None:
            name = dataRaw["package"]["author"].lower() + "." + name
        if dataRaw["package"].get("version") != None:
            name = name + "." + dataRaw["package"]["version"].lower()
    return name

def _getInstalledModuloPackages(path=str, exclusionPathList=list, travelSymlink=False, encoding="utf-8"):
    """Function to return the name of al installed modulo packages, since file should be either <installedFolderName>.<fileExt> or <packageName>.<fileExt>
    Note! Symlinks are always ignored inside collection-entries!
    Nested collections are not allowed either!"""
    topLevelFolders = getFoldersInPath(path,travelSymlink) # Get each folder in packages-path
    installedPackages = []
    for topLevel in topLevelFolders:
        if topLevel not in exclusionPathList:
            # setup possebilities
            possibleCollectionConfig = os.path.join(topLevel,"collection.json")
            possiblePackageConfig = os.path.join(topLevel, "package.json")
            # Collection
            if os.path.exists(possibleCollectionConfig):
                collectionData = _fileHandler(filesys.getFileExtension(possibleCollectionConfig),"get",possibleCollectionConfig,encoding=encoding)
                if collectionData.get("entries") != None:
                    for entry in collectionData["entries"]:
                        # resolve ./ paths
                        _replaceable = topLevel
                        if not _replaceable.endswith("/"): _replaceable += os.sep
                        elif not _replaceable.endswith("\\"): _replaceable += os.sep
                        if entry.startswith("./"):
                            entry = entry.replace("./",f"{topLevel}")
                        elif entry.startswith(".\\"):
                            entry = entry.replace(".\\",f"{topLevel}")
                        # resolve just foldernames
                        if "/" not in entry and "\\" not in entry:
                            entry = os.path.join(_replaceable,entry)
                        entry = os.path.abspath(entry)
                        # check exi
                        if os.path.exists(entry) and os.path.isdir(entry) and entry not in exclusionPathList:
                            possiblePackageConfigForCollectionEntry = os.path.join(entry,"package.json")
                            name = _getNameOfModuloPackage(possiblePackageConfigForCollectionEntry,encoding=encoding,fileIsStream=False)
                            installedPackages.append({
                                "name": name,
                                "path": entry
                            })                       
            # Packages
            elif os.path.exists(possiblePackageConfig):
                name = _getNameOfModuloPackage(possiblePackageConfig,encoding=encoding,fileIsStream=False)
                installedPackages.append({
                    "name": name,
                    "path": topLevel
                })
    # Return
    return installedPackages

def discoverInstalledPackages(type_,exclusions=list,installDest=str,legacyTraverseDepth=1,travelSymlink=False,moduloEncoding="utf-8"):
    installedPackages = {
        "names": [],
        "pnames": [],
        "paths": []
    }
    if type_ == "legacy":
        _paths = _getInstalledLegacyPackages(installDest,exclusions, traverseDepth=legacyTraverseDepth, travelSymlink=travelSymlink)
        for _path in _paths:
            installedPackages["paths"].append(_path)
            installedPackages["names"].append(os.path.abspath(_path).split(os.sep)[-1])
        del _paths
    elif type_ == "modulo":
        _datas = _getInstalledModuloPackages(installDest,exclusions, travelSymlink=travelSymlink, encoding=moduloEncoding)
        for _data in _datas:
            installedPackages["paths"].append(_data["path"])
            installedPackages["pnames"].append(os.path.abspath(_data["path"]).split(os.sep)[-1])
            installedPackages["names"].append(_data["name"])
        del _datas
    return installedPackages

def discoverPackageFiles(type_=str, sourcePath=str|object, installDest=str, fileExtensions=list, excludedFolders=list, legacyDiscoverTraverseDepth=1, travelSymlink=False, moduloEncoding="utf-8"):
    """Discovers package files that aren't installed"""
    type_ = type_.lower()
    if type_ not in ["modulo","legacy"]:
        raise Exception(f"Invalid package-type '{type_}' ")
    if type(sourcePath) == str:
        sourcePaths = [sourcePath]
    else:
        sourcePaths = sourcePath.get() # for assumed pathObjs
    # Get a list of files in the source path filtered by the extensions
    packageFiles = []
    for path in sourcePaths:
        packageFiles.extend(
            GetFilesByExt(path, fileExtensions)
        )
    # Get a list of installed packages to match with
    _exclusions = [*sourcePaths,*excludedFolders]
    installedPackages = discoverInstalledPackages(type_,_exclusions,installDest,legacyDiscoverTraverseDepth,travelSymlink,moduloEncoding)
    # Check if a packages are installed and filter them out
    noninstalledPackageFiles = []
    for package in packageFiles:
        filename = list(package.keys())[0]
        filepath = package[filename]
        # legacy
        if type_ == "legacy":
            if filename not in installedPackages["names"]:
                noninstalledPackageFiles.append(filepath)
        # modulo
        elif type_ == "modulo":
            if filename not in installedPackages["names"] and filename not in installedPackages["pnames"]:
                noninstalledPackageFiles.append(filepath)
    # return
    return noninstalledPackageFiles,installedPackages["paths"]

def installPackageFiles(nonInstalledPackages=dict,installedPackages=dict,installDestModulo=str,installDestLegacy=str):
    """Installs package files. (uncompresses them to right folder and adds them to "installed" list)"""
    # install modulo
    if nonInstalledPackages.get("modulo") != None:
        for packageFile in nonInstalledPackages["modulo"]:
            pathOnly = os.path.dirname(packageFile)
            fileName = filesys.getFileName(packageFile)
            newPath = os.path.join(pathOnly,f"{fileName}.zip")
            filesys.renameFile(packageFile,newPath) # rename to zip
            try:
                destPath = os.path.join(installDestModulo,fileName)
                filesys.ensureDirPath(destPath)
                filesys.unArchive(newPath,destPath)
                filesys.renameFile(newPath,packageFile) # rename to mpack again
                installedPackages["modulo"].append(destPath)
            except:
                print(f"Failed to load modulo-package '{packageFile}', invalid archive!")
                filesys.renameFile(newPath,packageFile) # rename to mpack again
    # install legacy
    if nonInstalledPackages.get("legacy") != None:
        for packageFile in nonInstalledPackages["legacy"]:
            pathOnly = os.path.dirname(packageFile)
            fileName = filesys.getFileName(packageFile)
            newPath = os.path.join(pathOnly,f"{fileName}.zip")
            filesys.renameFile(packageFile,newPath) # rename to zip
            try:
                destPath = os.path.join(installDestLegacy,fileName)
                filesys.ensureDirPath(destPath)
                filesys.unArchive(newPath,destPath)
                filesys.renameFile(newPath,packageFile) # rename to mpack again
                installedPackages["legacy"].append(destPath)
            except:
                print(f"Failed to load legacy-package '{packageFile}', invalid archive!")
                filesys.renameFile(newPath,packageFile) # rename to mpack again
    return installedPackages

def loadPackageConfig(installedPackages,defaultFeatures=dict,encoding="utf-8"):
    packageConfigs = {
        "modulo": {},
        "legacy": {}
    }
    foundFeatures = defaultFeatures
    # modulo
    for type_ in installedPackages.keys():
        for packagePath in installedPackages[type_]:
            possiblePackageConfig = os.path.join(packagePath, "package.json")
            if os.path.exists(possiblePackageConfig):
                packageName = _getNameOfModuloPackage(possiblePackageConfig,encoding=encoding)
                packageData = _fileHandler("json","get",possiblePackageConfig,encoding=encoding)
                packageConfigs[type_][packageName] = packageData
                if packageData.get("features") != None:
                    foundFeatures[packageName] = packageData["features"] 
    return packageConfigs,foundFeatures

def normFeatureDataAndReg(foundFeatures,registerMethod,allowedFeatureTypes):
    for package,featuresData in foundFeatures.items():
        for featureName,featureData in featuresData.items():
            if featureData.get("registeredBy") == None:
                featureData["registeredBy"] = package
            if featureData.get("legacy_addr") == None:
                featureData["legacy_addr"] = None
            if featureData.get("recursive") == None:
                featureData["recursive"] = False
            #addr
            addr = featureData.get("addr")
            if addr in [None,""]: addr = "/"
            if addr.startswith("./"): addr = addr.replace("./","/",1)
            addr = addr.replace("\\","/")
            if not addr.startswith("/"): addr = "/" + addr
            featureData["addr"] = addr
            #laddr
            laddr = featureData.get("legacy_addr")
            if laddr != None:
                if laddr == "": laddr = "/"
                if laddr.startswith("./"): laddr = laddr.replace("./","/",1)
                laddr = laddr.replace("\\","/")
                if not laddr.startswith("/"): laddr = "/" + laddr
                featureData["legacy_addr"] = laddr
            # register
            if featureData.get("type") in allowedFeatureTypes and featureData.get("addr") not in ["",None]:
                registerMethod(featureName,featureData)
