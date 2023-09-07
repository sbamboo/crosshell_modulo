import os
from ..externalLibs.filesys import filesys as fs
from ..cslib import handleOSinExtensionsList,_fileHandler
from .legacy import getDataFromList as legacy_getDataFromList

def getDataFromList(
    langpck_pathObj,
    langpck_provider,
    cmdlets_confFileExts=["cfg","config","conf"],
    cmdlets_rootFileExts=["json","cfg","conf","config"],
    crshparentPath=str,packages=list,registry=list,encoding="utf-8"
):
    # Load readerdata
    readerData = registry["readerData"]
    # Iterate over packages
    for package in packages:
        source = None
        # Modules
        source = f"{package}{os.sep}Modules"
        if os.path.exists(source):
            pass
        # Injects
        source = f"{package}{os.sep}Injects"
        if os.path.exists(source):
            pass
        # Plugins
        source = f"{package}{os.sep}Plugins"
        if os.path.exists(source):
            pass
        # Langpck
        source = f"{package}{os.sep}Langpck"
        if os.path.exists(source):
            langpck_pathObj.extend([source])
            langpck_provider.populateList()
        # Scripts
        source = f"{package}{os.sep}Scripts"
        if os.path.exists(source):
            pass
        # Readers
        source = f"{package}{os.sep}Readers"
        if os.path.exists(source):
            readerJSONpath = f"{source}{os.sep}readers.json"
            if os.path.exists(readerJSONpath):
                readerJSON = _fileHandler("json","get",readerJSONpath,encoding=encoding,safeSeps=True)
                for key,extensions in readerJSON.items():
                    readerFile = f"{source}{os.sep}{key}.py"
                    if os.path.exists(readerFile):
                        readerData = {"name":key,"exec":readerFile,"extensions":extensions}
                        registry["readerData"].append(readerData)
        # Cmdlets
        source = f"{package}{os.sep}Cmdlets"
        if os.path.exists(source):
            registry["cmdlets"] = legacy_getDataFromList(
                crshparentPath=crshparentPath,
                packages=[source],
                registry=registry,
                encoding=encoding,
                confFileExts=cmdlets_confFileExts,
                rootFileExts=cmdlets_rootFileExts
            )
    # Return
    return registry