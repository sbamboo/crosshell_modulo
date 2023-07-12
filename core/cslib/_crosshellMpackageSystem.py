'''
CSlib: CrosshellMpackageSystem contains crosshells code to handle modules.
'''

import os
from .externalLibs.filesys import filesys

def _getMPackageFiles(Path=str,packageExtensions=list):
    packageFiles = []
    objects = filesys.scantree(Path)
    for object in objects:
        fending = filesys.getFileExtension(object.name)
        name = filesys.getFileName(object.name)
        if fending in packageExtensions:
            packageFiles.append({name:object.path})
    return packageFiles

def _findInstalledPackages(Path=str):
    packages = []
    objects = filesys.scantree(Path)
    for object in objects:
        if filesys.isDir(object.path) == True:
            packages.append(object.name)
    return packages

def _listUninstalledPackages(packageFiles=list,installedPackages=list):
    '''not used'''
    uninstalledPackages = []
    for package in packageFiles:
        if list(package.keys())[0] not in installedPackages:
            uninstalledPackages.append(package)
    return uninstalledPackages


def loadPackages(PackageFilePathObject,PackagesPathObject,packageExtensions=["mpackage","mpack","mPackage","mPack"]):
    '''CSlib.CMPS: finds and installs packages, finally returing a list of al installed packages on the system'''
    # Find .mpackage files
    filePaths = PackageFilePathObject.get()
    packageFiles = []
    for path in filePaths:
        packageFiles.extend(_getMPackageFiles(path,packageExtensions))
    # Look at the list of installed mpackages (folders)
    packsPaths = PackagesPathObject.get()
    installedPackages = []
    for path in packsPaths:
        installedPackages.extend(_findInstalledPackages(path))
    # Extract uninstalled mpackages
    for package in packageFiles:
        if list(package.keys())[0] not in installedPackages:
            path = list(package.values())[0]
            pathOnly = os.path.dirname(path)
            fileName = filesys.getFileName(path)
            newPath = f"{pathOnly}{os.sep}{fileName}.zip"
            filesys.renameFile(path,newPath)
            try:
                filesys.unArchive(newPath,packsPaths[0])
            except:
                print(f"Failed to load mPackage '{path}', invalid archive!")
                filesys.renameFile(newPath,path)
    # Return a list of paths of installed packages