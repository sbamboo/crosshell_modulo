'''
CSlib: CrosshellMpackageSystem contains crosshells code to handle modules.
'''

import os
from .externalLibs.filesys import filesys

def _getPackageFiles(Path=str,packageExtensions=list):
    packageFiles = []
    objects = filesys.scantree(Path)
    for object in objects:
        fending = filesys.getFileExtension(object.name)
        name = filesys.getFileName(object.name)
        if fending.lower() in packageExtensions:
            packageFiles.append({name:object.path})
    return packageFiles

def _findInstalledPackages(Path=str,exclusionList=list,safeMode=False):
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

def _listNoninstalledPackages(packageFiles=list,installedPackages=list):
    '''not used'''
    NoninstalledPackages = []
    for package in packageFiles:
        if list(package.keys())[0] not in installedPackages:
            NoninstalledPackages.append(package)
    return NoninstalledPackages

def loadPackages(findFilesPathObj,DestinationPath=str,packageExtensions=list):
    '''CSlib.CMPS: finds and installs packages, finally returing a list of al installed packages.'''
    # Find files
    filePaths = findFilesPathObj.get()
    packageFiles = []
    for path in filePaths:
        packageFiles.extend(_getPackageFiles(path,packageExtensions))
    # Retrive a list of al installed packages
    installedPackages = []
    installedPackages.extend(_findInstalledPackages(DestinationPath,findFilesPathObj.get()))
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


# Function to create a registry entry for a legacyCmdlet.
def loadLegacyCmdlet(PackagePath) -> dict:
    '''CSlib.CMPS: Creates a registry entry for a legacyCmdlet'''
    # Find files
    # Check if they have a package.yaml file storing config for the cmdlets
    # Look at <cmdletName>.cfg / <cmdletName>.config files
    # Create a registry entry / dict for the cmdlet
    # Return a dictionary with al cmdletRegistryEntries as nested dicts