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
            if not any(part.startswith('.') for part in fillPath.split(os.path.sep)):
                nonHiddenFolders.append(fillPath)
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
    name = filesys.getFileName(configFilepath)
    if dataRaw.get("package") != None:
        if dataRaw["package"].get("name") != None:
            name = dataRaw["package"]["name"]
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
    installedPackages = {
        "names": [],
        "pnames": []
    }
    _exclusions = [*sourcePaths,*excludedFolders]
    if type_ == "legacy":
        _paths = _getInstalledLegacyPackages(installDest,_exclusions, traverseDepth=legacyDiscoverTraverseDepth, travelSymlink=travelSymlink)
        for _path in _paths:
            installedPackages["names"].append(os.path.abspath(_path).split(os.sep)[-1])
        del _paths
    elif type_ == "modulo":
        _datas = _getInstalledModuloPackages(installDest,_exclusions, travelSymlink=travelSymlink, encoding=moduloEncoding)
        for _data in _datas:
            installedPackages["pnames"].append(os.path.abspath(_data["path"]).split(os.sep)[-1])
            installedPackages["names"].append(_data["name"])
        del _datas
    # Check if a packages are installed and filter them out
    noninstalledPackageFiles = []
    for package in packageFiles:
        filename = package.keys()[0]
        filepath = package[filename]
        # legacy
        if type_ == "legacy":
            if filename not in installedPackages["names"]:
                noninstalledPackageFiles.append(filepath)
        # modulo
        elif type_ == "modulo":
            if filename not in installedPackages["names"] and filename not in installedPackages["panmes"]:
                noninstalledPackageFiles.append(filepath)
    # return
    return noninstalledPackageFiles