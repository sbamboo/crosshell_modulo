'''
CSlib: CrosshellMpackageSystem contains crosshells code to handle modules.
'''

import os
import json
from .externalLibs.filesys import filesys
from .datafiles import _fileHandler
from ._crosshellParsingEngine import pathtagmanager_parseDict

def _getPackageFiles(Path=str,packageExtensions=list):
    packageFiles = []
    objects = filesys.scantree(Path)
    for object in objects:
        fending = filesys.getFileExtension(object.name)
        name = filesys.getFileName(object.name)
        if fending.lower() in packageExtensions:
            packageFiles.append({name:object.path})
    return packageFiles

def _findInstalledPackages_depricated(Path=str,exclusionList=list,safeMode=False):
    packages = []
    objects = filesys.scantree(Path)
    for object in objects:
        if safeMode == True:
            dirname = os.path.dirname(object.path)
            if os.path.dirname(dirname) == Path and dirname not in packages:
                if dirname not in exclusionList:
                    packages.append(dirname)
        else:
            if filesys.isDir(object.path) == True:
                packages.append(object.name)
    return packages

def list_non_hidden_folders(path, max_depth=None):
    non_hidden_folders = []
    for root, dirs, _ in os.walk(path):
        if max_depth is not None and root.count(os.path.sep) - path.count(os.path.sep) >= max_depth:
            continue
        for dir_name in dirs:
            full_path = os.path.join(root, dir_name)
            if not any(part.startswith('.') for part in full_path.split(os.path.sep)):
                non_hidden_folders.append(full_path)

    return non_hidden_folders

def _findInstalledPackages(Path=str,exclusionList=list,traverseDepth=None):
    packages = []
    paths = list_non_hidden_folders(Path,traverseDepth)
    for dir in paths:
        if dir not in exclusionList and dir != Path:
            if dir not in packages:
                packages.append(dir)
    return packages

def _listNoninstalledPackages(packageFiles=list,installedPackages=list):
    '''not used'''
    NoninstalledPackages = []
    for package in packageFiles:
        if list(package.keys())[0] not in installedPackages:
            NoninstalledPackages.append(package)
    return NoninstalledPackages

def loadPackages(findFilesPathObj,DestinationPath=str,packageExtensions=list,findTraverseDepth=1,extraExclusions=None):
    '''CSlib.CMPS: finds and installs packages, finally returing a list of al installed packages.'''
    # Find files
    filePaths = findFilesPathObj.get()
    packageFiles = []
    for path in filePaths:
        packageFiles.extend(_getPackageFiles(path,packageExtensions))
    # Retrive a list of al installed packages
    installedPackages = []
    exclusions = filePaths.copy()
    if extraExclusions is not None:
        exclusions.extend(extraExclusions)
    installedPackages.extend(_findInstalledPackages(DestinationPath,exclusions,findTraverseDepth))
    # Extract uninstalled mpackages and add them to the list
    for package in packageFiles:
        if list(package.keys())[0] not in installedPackages:
            path = list(package.values())[0]
            pathOnly = os.path.dirname(path)
            fileName = filesys.getFileName(path)
            newPath = f"{pathOnly}{os.sep}{fileName}.zip"
            filesys.renameFile(path,newPath)
            try:
                destinationPath = f"{DestinationPath}{os.sep}{fileName}"# Index 0 for default path
                filesys.ensureDirPath(destinationPath)
                filesys.unArchive(newPath,destinationPath)
                filesys.renameFile(newPath,path) # Rename to mpackage from zip again
                installedPackages.append(destinationPath)
            except:
                print(f"Failed to load package '{path}', invalid archive!")
                filesys.renameFile(newPath,path)
    # Return a list of paths of installed packages
    return installedPackages

def getPackageData(packagePath,encoding="utf-8"):
    # setup priority (first is; top-prio = [0])
    keys = ["package","mpackage","cspackage","crsh"]
    # get file
    possiblePackageFile = f"{packagePath}{os.sep}package.json"
    if os.path.exists(possiblePackageFile):
        # get content
        content = _fileHandler("json","get",possiblePackageFile,encoding=encoding)
        # check for keyname
        data = {}
        for key in keys:
            if content.get(key) != None:
                data = content.get(key)
                break
        # return
        return data

def getPackageDataFromList(packageList,encoding="utf-8"):
    packageData = []
    for key,value in packageList.items():
        for p in value:
            # get name
            name = os.path.basename(p)
            # set base data
            pdict = {name:{"path":p,"type":key}}
            # get data
            _data = getPackageData(p,encoding)
            if _data != None:
                pdict[name].update(_data)
            # append
            packageData.append(pdict)
    return packageData

def getDataForPackage(packageName,registry,filterType=None):
    reg_pdata = registry.get("packageData")
    if reg_pdata != None:
        for p in reg_pdata:
            vZ = list(p.values())[0]
            if filterType != None:
                if packageName in p.keys() and vZ["type"] == filterType:
                    return vZ
            else:
                if packageName in p.keys():
                    return vZ