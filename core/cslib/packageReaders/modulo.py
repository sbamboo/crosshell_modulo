import os
from ..externalLibs.filesys import filesys as fs
from ..cslib import _fileHandler,normalizePathSep
from .legacy import getDataFromList as legacy_getDataFromList

def _formatReplNameTo(name=str) -> str:
    return name.replace(".","-")

def _formatReplNameFrom(name=str) -> str:
    return name.replace("-",".")

def getDataFromList(
    CS_Settings,
    CS_ModuleReplacebles,
    langpck_pathObj,
    langpck_provider,
    cmdlets_confFileExts=["cfg","config","conf"],
    cmdlets_rootFileExts=["json","cfg","conf","config"],
    crshparentPath=str,packages=list,registry=list,encoding="utf-8"
):
    # Load readerdata
    readerData = registry["readerData"]
    # add selected replace-file presets to settings
    replaceables = CS_ModuleReplacebles.keys()
    for replaceable in replaceables:
        CS_Settings.addProperty("crsh", f"Modules.Files.{_formatReplNameTo(replaceable)}.selection", None)
        CS_Settings.chnProperty("crsh", f"Modules.Files.{_formatReplNameTo(replaceable)}._choices", None)
    # Iterate over packages
    for package in packages:
        source = None
        # Modules
        source = f"{package}{os.sep}Modules"
        if os.path.exists(source):
            replaceJSONpath = f"{source}{os.sep}replace.json"
            if os.path.exists(replaceJSONpath):
                replaceJSON = _fileHandler("json","get",replaceJSONpath,encoding=encoding,safeSeps=False)
                avsToReplace = {}
                for name,value in replaceJSON.items():
                    key = value["toReplace"]
                    value = value["replaceWith"]
                    value = value.replace("{parent}",source)
                    value = normalizePathSep(value)
                    # does it replace a replaceable?
                    if key in replaceables:
                        if avsToReplace.get(key) == None: avsToReplace[key] = {}
                        avsToReplace[key][name] = value
                # add choices to settings
                for toreplace,replaceable in avsToReplace.items():
                    choices = CS_Settings.getProperty("crsh", f"Modules.Files.{_formatReplNameTo(toreplace)}._choices")
                    if choices == None: choices = []
                    choices.extend(list(replaceable.keys()))
                    CS_Settings.chnProperty("crsh", f"Modules.Files.{_formatReplNameTo(toreplace)}._choices", choices)
                # get selected
                for repl in replaceables:
                    selection = CS_Settings.getProperty("crsh", f"Modules.Files.{_formatReplNameTo(toreplace)}.selection")
                    nonAllowed = [None,"None","none","Null","null","","int","INT","internal","INTERNAL","def","DEF","default","DEFAULT"]
                    if selection not in nonAllowed:
                        toReplaceWidth = avsToReplace[repl][selection]
                        CS_ModuleReplacebles[repl]["obj"].load(toReplaceWidth)

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
                settings=CS_Settings,
                crshparentPath=crshparentPath,
                packages=[source],
                registry=registry,
                encoding=encoding,
                confFileExts=cmdlets_confFileExts,
                rootFileExts=cmdlets_rootFileExts
            )
    # Return
    return registry