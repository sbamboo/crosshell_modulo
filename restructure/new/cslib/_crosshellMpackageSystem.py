'''
CSlib: CrosshellMpackageSystem contains crosshells code to handle modules.
'''

import os
from cslib.datafiles import _fileHandler,config_to_dict
from cslib.externalLibs.filesys import filesys
from cslib.pathtools import normPathSep
from cslib.types import expectedList
from cslib.piptools import fromPath
from cslib.platformAndOS import handleOSinExtensionsList

def idToDict(idstr) -> dict:
    """
    Parses: <feature>@<prefix>:<pkgAuthor>.<pkgName>.<pkgVersion>/<relativePath>
    """
    # preset
    data = {
        "feature": None,
        "package": {
            "author": None,
            "name": None,
            "version": None,
            "prefix": None,
            "id": None
        },
        "path": None
    }
    # set
    idstr = idstr.lstrip(" ")
    ## relpath
    if idstr.startswith("/"):
        data["path"] = idstr.replace("/","",1)
    else:  
        ## dupeID
        if idstr.startswith("#"):
            idstr = idstr.replace("#","",1)
        elif "#" in idstr:
            if idstr.split("#")[-1].isdigit():
                data["package"]["id"] = idstr.split("#")[-1]
                idstr = '#'.join(idstr.split("#")[:-1])
        ## path
        if "/" in idstr:
            parts = idstr.split("/")
            idstr = parts[0]
            data["path"] = '/'.join(parts[1:])
            if not data["path"].startswith("/"): data["path"] = "/" + data["path"]
        ## feature
        if idstr.startswith("@"):
            idstr = idstr.replace("@","",1)
        elif "@" in idstr:
            data["feature"] = idstr.split("@")[0]
            idstr = '@'.join(idstr.split("@")[1:])
        ## prefix
        if idstr.startswith(":"):
            idstr = idstr.replace(":","",1)
        elif ":" in idstr:
            data["package"]["prefix"] = idstr.split(":")[0]
            idstr = ':'.join(idstr.split(":")[1:])
        ## details
        if idstr.count(".") > 1:
            parts = idstr.split(".")
            data["package"]["author"] = parts[0]
            parts.pop(0)
            data["package"]["name"] = '.'.join(parts[:-1])
            data["package"]["version"] = parts[-1]
        elif "." in idstr:
            data["package"]["name"] = '.'.join(idstr.split(".")[:-1])
            data["package"]["version"] = idstr.split(".")[-1]
        else:
            data["package"]["name"] = idstr
    # return
    return data

def toLeastInfoStr(gid,mgids) -> str:
    names = []
    versions = []
    authors = []
    prefixs = []
    ids = []
    for gid2 in mgids:
        if gid2 != gid:
            _t = idToDict(gid2)
            if _t["package"]["name"] != None: names.append(_t["package"]["name"])
            if _t["package"]["version"] != None: versions.append(_t["package"]["version"])
            if _t["package"]["author"] != None: authors.append(_t["package"]["author"])
            if _t["package"]["prefix"] != None: prefixs.append(_t["package"]["prefix"])
            if _t["package"]["id"] != None: ids.append(_t["package"]["id"])
    gid = idToDict(gid)
    name_ = gid["package"]["name"]
    version_ = gid["package"]["version"]
    author_ = gid["package"]["author"]
    prefix_ = gid["package"]["prefix"]
    id_ = gid["package"]["id"]
    path_ = gid["path"]
    # made
    if name_ in names:
        if version_ in versions:
            if author_ in authors:
                if feature_ in features:
                    if prefix_ in prefixs:
                        least = feature_+"@"+prefix_+":"+author_+"."+name_+"."+version_+"#"+id_
                    else:
                        least = feature_+"@"+prefix_+":"+author_+"."+name_+"."+version_    
                else:
                    least = feature_+"@"+author_+"."+name_+"."+version_    
            else:
                least = author_+"."+name_+"."+version_    
        else:
            least = name_+"."+version_
    else:
        least = name_
    # return
    return least+path_

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

def listNonHiddenFolders(path, maxDepth=None, travelSymlink=False) -> list:
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

def listFilesOfType(directory, fileTypes, givePaths=True):
    filesOfType = []
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            if any(file.endswith("." + fileType) for fileType in fileTypes):
                if givePaths == True:
                    filesOfType.append( os.path.join(directory,file) )
                else:
                    filesOfType.append(file)
    return filesOfType

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
    gidd = idToDict(name)
    if dataRaw.get("package") != None:
        if dataRaw["package"].get("name") != None:
            gidd["package"]["name"] = dataRaw["package"]["name"]
        elif dataRaw["package"].get("author") != None:
            gidd["package"]["author"] = dataRaw["package"]["author"].lower()
        elif dataRaw["package"].get("version") != None:
            gidd["package"]["version"] = dataRaw["package"]["version"].lower()
    if gidd["package"]["name"] != None:
        name = gidd["package"]["name"]
    if gidd["package"]["author"] != None:
        name = gidd["package"]["author"]+"."+name
    if gidd["package"]["version"] != None:
        name = name+"."+gidd["package"]["version"]
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
                packageConfigs[type_][packageName]["path"] = packagePath
                if packageData.get("features") != None:
                    foundFeatures[type_+"@"+packageName] = packageData["features"]
    return packageConfigs,foundFeatures

def normPathsInFeatureData(path) -> str:
    if path in [None,""]: path = "/"
    path = path.replace("\\","/")
    if path.startswith("./"): path = path.replace("./","/",1)
    if not path.startswith("/"): path = "/" + path
    return path

def normFeatureDataAndReg(foundFeatures,registerMethod,allowedFeatureTypes):
    for packageID,featuresData in foundFeatures.items():
        if "@" in packageID:
            package = packageID.split("@")[1]
            packageType = packageID.split("@")[0]
        else:
            package = packageID
            packageType = None
        for featureName,featureData in featuresData.items():
            if featureData.get("registeredBy") == None:
                featureData["registeredBy"] = package
            if featureData.get("registeredByType") == None:
                featureData["registeredByType"] = packageType
            if featureData.get("legacy_addr") == None:
                featureData["legacy_addr"] = None
            if featureData.get("recursive") == None:
                featureData["recursive"] = False
            if featureData.get("inclDotted") == None:
                featureData["inclDotted"] = False
            if featureData.get("folderExclusions") == None:
                featureData["folderExclusions"] = []
            if featureData.get("mappingFileType") == None:
                featureData["mappingFileType"] = "DEFAULT"
            if featureData.get("mangler") == None:
                featureData["mangler"] = None
            if featureData.get("manglerKwargs") == None:
                featureData["manglerKwargs"] = None
            #addr
            #addr = featureData.get("addr")
            #if addr in [None,""]: addr = "/"
            #if addr.startswith("./"): addr = addr.replace("./","/",1)
            #addr = addr.replace("\\","/")
            #if not addr.startswith("/"): addr = "/" + addr
            #featureData["addr"] = addr
            featureData["addr"] = normPathsInFeatureData(featureData.get("addr"))
            #laddr
            laddr = featureData.get("legacy_addr")
            if laddr != None:
                #if laddr == "": laddr = "/"
                #if laddr.startswith("./"): laddr = laddr.replace("./","/",1)
                #laddr = laddr.replace("\\","/")
                #if not laddr.startswith("/"): laddr = "/" + laddr
                laddr = normPathsInFeatureData(laddr)
                featureData["legacy_addr"] = laddr
            # folderExclusions
            if featureData.get("folderExclusions") != None:
                for i,path in enumerate(featureData["folderExclusions"]):
                    featureData["folderExclusions"][i] = normPathsInFeatureData(path)
            # register
            typeAllowed = False
            typeToAllowCheck = featureData.get("type")
            if ":" in typeToAllowCheck:
                baseType = typeToAllowCheck.split(":")[0].rstrip(" ")
                for type_ in allowedFeatureTypes:
                    if ":" in type_ and baseType == type_.split(":")[0].rstrip(" "):
                        typeAllowed = True
            else:
                if typeToAllowCheck in allowedFeatureTypes:
                    typeAllowed = True
            if typeAllowed == True and featureData.get("addr") not in ["",None]:
                registerMethod(featureName,featureData)

def loadPackageFeatures(loadedFeatures,packageConfigs,maxRecursiveDepth=None,travelSymlink=False,defaultFeatureConfigType="json",mappingFileEncoding="utf-8",preLoadedReaders={},preLoadedReadersType="modulo",preLoadedReadersFeature="readers",legacyPackagePath=str,moduloPackagePath=str):
    if preLoadedReaders not in [None,{}]:
        if loadedFeatures[preLoadedReadersFeature]["data"].get(preLoadedReadersType) == None: loadedFeatures[preLoadedReadersFeature]["data"][preLoadedReadersType] = {}
        loadedFeatures[preLoadedReadersFeature]["data"][preLoadedReadersType]["builtins"] = preLoadedReaders
    # Iterate over al features
    for featureName, featureData in loadedFeatures.items():
        # Get feature data
        featureConfig = featureData["config"]
        featureType = featureConfig["type"].lower()
        featureAddr = featureConfig["addr"]
        featureLegacyAddr = featureConfig["legacy_addr"]
        featureRecursive = featureConfig["recursive"]
        featureIncludeDotted = featureConfig["inclDotted"]
        featureExclusions = featureConfig["folderExclusions"]
        featureMappingFileType = featureConfig["mappingFileType"]
        featureMangler = featureConfig["mangler"]
        featureManglerKwargs = featureConfig["manglerKwargs"]
        if featureMappingFileType == None or featureMappingFileType.lower() == "default":
            featureMappingFileType = defaultFeatureConfigType
        # Iterate over package types
        for packageType, configs in packageConfigs.items():
            # Iterate over packages
            for packageName,packageConfig in configs.items():
                if loadedFeatures[featureName]["data"].get(packageType) == None: loadedFeatures[featureName]["data"][packageType] = {}
                if packageType == "legacy":
                    address = featureLegacyAddr
                else:
                    address = featureAddr
                # Legacy adresses might be None to disable legacy-support so in that case skip
                if address != None:
                    addressPath_partAddress = normPathSep(address)
                    addressPath_partPkgPth = normPathSep(packageConfig["path"])
                    # Ensure that the packagePath dosen't end with sep
                    if addressPath_partPkgPth.endswith(os.sep):
                        addressPath_partPkgPth = (addressPath_partPkgPth[::-1].replace(os.sep,"",1))[::-1]
                    # If adress != sep apply it
                    if addressPath_partAddress != os.sep:
                        # Ensure that the adressPath 
                        if not addressPath_partAddress.startswith(os.sep):
                            addressPath_partAddress = os.sep + addressPath_partAddress
                        # Join the two
                        addressPath = addressPath_partPkgPth + addressPath_partAddress
                    # If not just set it to the root
                    else:
                        addressPath = addressPath_partPkgPth
                    # Discover search-directories 
                    searchDirs = []
                    if os.path.exists(addressPath) == True:
                        searchDirs.append(addressPath)
                        # Recursive
                        if featureRecursive != False:
                            searchDirs.extend(listNonHiddenFolders(addressPath,maxRecursiveDepth,travelSymlink))
                    # Load data based on type
                    ## Raw
                    if "raw" in featureType:
                        featureFileName = featureName
                        if ":" in featureType:
                            featureFileName = featureType.split(":")[1].strip()
                        dataFile = featureFileName+"."+featureMappingFileType
                        mappingFtype = featureMappingFileType.lower()
                        if (mappingFtype == "yml"): mappingFtype = "yaml"# Iterate over the search directories and look for mappings file
                        for sdir in searchDirs:
                            mappingFilePath = os.path.join(sdir,dataFile)
                            if os.path.exists(mappingFilePath):
                                mappingFileData = {}
                                # If file was found load it and add the data based on the mapping_type
                                if mappingFtype in ["cfg","config","property","properties"]:
                                    mappingFileData = config_to_dict(
                                        open(mappingFilePath,'r',encoding=encoding).read()
                                    )
                                elif mappingFtype in ["json","yaml"]:
                                    mappingFileData = _fileHandler(mappingFtype,"get",mappingFilePath,encoding=mappingFileEncoding)
                                if mappingFileData not in ["",None,{},[]]:
                                    if loadedFeatures[featureName]["data"][packageType].get(packageName) == None: loadedFeatures[featureName]["data"][packageType][packageName] = {}
                                    loadedFeatures[featureName]["data"][packageType][packageName].update(mappingFileData)
                    ## Mappings
                    elif "mapping" in featureType:
                        mappingFile = featureName+"."+featureMappingFileType
                        mappingFtype = featureMappingFileType.lower()
                        if (mappingFtype == "yml"): mappingFtype = "yaml"
                        # Iterate over the search directories and look for mappings file
                        for sdir in searchDirs:
                            mappingFilePath = os.path.join(sdir,mappingFile)
                            if os.path.exists(mappingFilePath):
                                mappingFileData = {}
                                # If file was found load it and add the data based on the mapping_type
                                if mappingFtype in ["cfg","config","property","properties"]:
                                    mappingFileData = config_to_dict(
                                        open(mappingFilePath,'r',encoding=encoding).read()
                                    )
                                elif mappingFtype in ["json","yaml"]:
                                    mappingFileData = _fileHandler(mappingFtype,"get",mappingFilePath,encoding=mappingFileEncoding)
                                # Handle filen/filep mappings
                                isRelPath = False
                                if featureType == "mapping_filen-1":
                                    isRelPath = True
                                    featureType = "mapping_1-1"
                                elif featureType == "mapping_filen-m":
                                    isRelPath = True
                                    featureType = "mapping_1-m"
                                # Load data based on mapping_type
                                if featureType == "mapping_1-1" or featureType == "mapping_filep-1":
                                    if len(list(mappingFileData.keys())) > 0:
                                        if loadedFeatures[featureName]["data"][packageType].get(packageName) == None: loadedFeatures[featureName]["data"][packageType][packageName] = {}
                                    for k,v in mappingFileData.items():
                                        if isRelPath == True: k = os.path.join(sdir,normPathSep(k))
                                        loadedFeatures[featureName]["data"][packageType][packageName][k] = v
                                elif featureType == "mapping_1-m" or featureType == "mapping_filep-m":
                                    if len(list(mappingFileData)) > 0:
                                        if loadedFeatures[featureName]["data"][packageType].get(packageName) == None: loadedFeatures[featureName]["data"][packageType][packageName] = {}
                                    for item in mappingFileData:
                                        if type(item) == str:
                                            if "=>" in item:
                                                _parts = item.split("=>")
                                                key = _parts[1].rstrip(" ")
                                                value = _parts[0].lstrip(" ")
                                            else:
                                                if "<=" in item: delim = "<="
                                                elif ": " in item: delim = ": "
                                                elif "=" in item: delim = "="
                                                _parts = item.split(delim)
                                                key = _parts[0].rstrip(" ")
                                                value = _parts[1].lstrip(" ")
                                        elif type(item) in [list,tuple]:
                                            key = item[0]
                                            value = item[1]
                                        elif type(item) == dict:
                                            key = item.keys()[0]
                                            value = item.values()[0]
                                        if loadedFeatures[featureName]["data"][packageType][packageName].get(k) == None:
                                            loadedFeatures[featureName]["data"][packageType][packageName][k] = []
                                        if isRelPath == True: k = os.path.join(sdir,normPathSep(k))
                                        loadedFeatures[featureName]["data"][packageType][packageName][k].append(value)
                    ## Registry
                    elif "registry" in featureType:
                        pre = featureType.split(":")[0]
                        pst = featureType.split(":")[1]
                        # For specific type
                        if pre == "registry_fortype":
                            if "," in pst:
                                pst = pst.split(",")
                            else:
                                pst = [pst]
                            for sdir in searchDirs:
                                typeTypes = handleOSinExtensionsList(pst)
                                filesOfTypes = listFilesOfType(sdir,pst,givePaths=False)
                                if filesOfTypes not in [None,[]]:
                                    if len(list(filesOfTypes)) > 0:
                                        if loadedFeatures[featureName]["data"][packageType].get(packageName) == None: loadedFeatures[featureName]["data"][packageType][packageName] = {}
                                    for file in filesOfTypes:
                                        ext = os.path.splitext(file)[1].lstrip(".")
                                        if loadedFeatures[featureName]["data"][packageType][packageName].get(ext) == None:
                                            loadedFeatures[featureName]["data"][packageType][packageName][ext] = []
                                        loadedFeatures[featureName]["data"][packageType][packageName][ext].append(file)
                        # For types given by another features data
                        elif pre == "registry_forfeature":
                            # Assemble complete-entries for feature
                            assembledData = {}
                            featureType_toread = loadedFeatures[pst]["config"]["type"].lower()
                            # Load mappings of 1-1 where its <smth>:<type/types>
                            if "mapping" in featureType_toread and featureType_toread.endswith("-1"):
                                for pkgType_toread in loadedFeatures[pst]["data"].keys():
                                    for readerEntry in loadedFeatures[pst]["data"][pkgType_toread].values():
                                        assembledData.update(readerEntry)
                            # Load mappings of 1-m where its <smth>:<type/types> (merges <smth> so multiple entries are ignored and latest is taken)
                            elif "mapping" in featureType_toread and featureType_toread.endswith("-m"):
                                for pkgType_toread in loadedFeatures[pst]["data"].keys():
                                    for readerEntry in loadedFeatures[pst]["data"][pkgType_toread].values():
                                        assembledData.update(readerEntry)
                            # Load mappings of raw where its just data
                            elif featureType_toread == "raw":
                                assembledData.update(loadedFeatures[pst]["data"][pkgType_toread])
                            # Find files of type per feature-entry
                            for sdir in searchDirs:
                                for parent,typeTypes in assembledData.items():
                                    if type(typeTypes) == str: typeTypes = [typeTypes]
                                    typeTypes = handleOSinExtensionsList(typeTypes)
                                    # Get al files of types and link to their parent
                                    filesOfTypes = listFilesOfType(sdir,typeTypes,givePaths=False)
                                    if filesOfTypes not in [None,[]]:
                                        if loadedFeatures[featureName]["data"][packageType].get(packageName) == None: loadedFeatures[featureName]["data"][packageType][packageName] = {}
                                        files_ = []
                                        for file_ in filesOfTypes:
                                            prefix = addressPath_partAddress.replace("\\","/")
                                            if not prefix.endswith("/"): prefix += "/"
                                            files_.append( prefix + file_ )
                                        loadedFeatures[featureName]["data"][packageType][packageName][parent] = files_
        # Apply mangling
        if featureMangler != None:
            featureMangler_toexec = None
            if type(featureMangler) == str:
                if "@" in featureMangler:
                    manglerFile = featureMangler.split("@")[0]
                    manglerFunc = featureMangler.split("@")[1]
                    if featureConfig["registeredByType"] == "legacy":
                        packagePath = os.path.join(legacyPackagePath,featureConfig["registeredBy"])
                    else:
                        packagePath = os.path.join(moduloPackagePath,featureConfig["registeredBy"])
                    manglerFile = normPathSep(manglerFile)
                    if manglerFile.startswith(os.sep):
                        manglerFile = manglerFile.replace(os.sep,"",1)
                    manglerFilePath = os.path.join(packagePath,manglerFile)
                    if os.path.exists(manglerFilePath):
                        try:
                            manglerModule = fromPath(manglerFilePath)
                            featureMangler_toexec = getattr(manglerModule, manglerFunc)
                        except: pass
            else:
                featureMangler_toexec = featureMangler
            if featureMangler_toexec != None:
                if featureManglerKwargs == None: featureManglerKwargs = {}
                mangledData = featureMangler_toexec(loadedFeatures[featureName]["data"],**featureManglerKwargs)
                if type(mangledData) == dict:
                    loadedFeatures[featureName]["data"] = mangledData

    # return
    return loadedFeatures
