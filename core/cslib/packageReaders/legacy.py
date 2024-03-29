import os,sys
from io import StringIO

from ..datafiles import config_to_dict,dict_to_config
from ..externalLibs.filesys import filesys as fs
from ..cslib import handleOSinExtensionsList,_fileHandler
from .._crosshellParsingEngine import pathtagManager_parse

def _toBool(value) -> bool:
    if type(value) == bool:
        return value
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False

def is_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file.read()
        return True
    except UnicodeDecodeError:
        return False
    except Exception as e:
        return False

def _getConfContent(conf_path=str,encoding="utf-8") -> dict:
    fending = fs.getFileExtension(conf_path)
    if fending == "json":
        return _fileHandler("json","get",conf_path,encoding=encoding)
    else:
        raw = open(conf_path,'r',encoding=encoding).read()
        return config_to_dict(raw)

def _getArgparseHelp(defa=str,path=str) -> str:
    fending = fs.getFileExtension(path)
    newHelp = defa
    if fending == "py":
        int_old_stdout = sys.stdout
        int_redirected_output = sys.stdout = StringIO()
        try:    exec(open(path).read(), {"argv":['--exhelp']})
        except  SystemExit as cs_cmdlet_exitcode: pass
        except: pass
        sys.stdout = int_old_stdout
        newHelp = int_redirected_output.getvalue()
    return newHelp

def _getSynopsisDesc(defa=str,path=str,encoding="utf-8") -> str:
    fending = fs.getFileExtension(path)
    newDesc = defa
    if fending == "ps1":
        raw_content = open(os.path.abspath(path),"r",encoding=encoding).read()
        split_content = raw_content.split("\n")
        try:
            if str(split_content[0]).strip() == "<#" and str(split_content[1]).strip() == ".SYNOPSIS":
                newDesc = str(split_content[2]).strip()
        except:
            pass
    return newDesc

def _parseCfgPathTags(string,package,path_of_config_file):
    if package.endswith("Cmdlets"):
        root = os.path.dirname(package)
    else:
        root = package
    tags = {
        "cmdlets": package,
        "cmdletsFolder": package,
        "parent": os.path.dirname(path_of_config_file),
        "root": root
    }
    return pathtagManager_parse(string,tags)

def getDataFromList(settings,crshparentPath=str,packages=list,registry=list,encoding="utf-8",confFileExts=["cfg","config","conf"],rootFileExts=["json","cfg","conf","config"],allowOldPackageFile=False):
    # OPT
    confFileExts = handleOSinExtensionsList(confFileExts)
    rootFileExts = handleOSinExtensionsList(rootFileExts)
    # Load readerdata
    readerData = registry["readerData"]
    # Complete list of fendings
    allowedFendings = []
    for reader in readerData:
        allowedFendings.extend( handleOSinExtensionsList(reader["extensions"]) )
    # go through and list for package.json/root.ycfg, then .cfg
    for package in packages:
        knownRootFiles = {} # <parent>:<file-path>
        # scan
        entries = fs.scantree(package)
        for entry in entries:
            if fs.isFile(entry.path) == True:
                confFile = None
                fex = fs.getFileExtension(entry.path)
                if fex != None:
                    fending = fs.getFileExtension(entry.path)
                else:
                    fending = None
                completePath = os.path.abspath(entry.path)
                cmdletPath = completePath.replace(crshparentPath,"")
                cmdletPath = cmdletPath.strip(os.sep)
                valid = True
                # dot in path validity
                for elem in cmdletPath.split(os.sep):
                    if str(elem) != "":
                        if str(elem)[0] == ".":
                            valid = False
                # dot in name validity
                if entry.name[0] == ".": valid = False
                # Handle platform-executable
                isPlatformExec = False
                if "MIME_EXECUTABLE" in allowedFendings and fending == None:
                    isPlatformExec = fs.isExecutable(entry.path)
                # check
                if isPlatformExec == True:
                    chck_fending = "MIME_EXECUTABLE"
                else:
                    if fending == None:
                        chck_fending = ""
                    else:
                        chck_fending = fending.lower()
                # Check for exec files
                if valid == True and chck_fending in allowedFendings:
                    regEntry = {
                        "name": fs.getFileName(entry.name),
                        "path": entry.path,
                        "fending": chck_fending,
                        "desc": "",
                        "aliases": [],
                        "args": "",
                        "blockCommonParameters": False,
                        "encoding": encoding,
                        "options": {
                            "argparseHelp": False,
                            "synopsisDesc": False,
                            "restrictionMode": "normal", #normal, internal, limited
                            "readerReturnVars": False,
                            "dontLoad": False
                        },
                        "extras" : {}
                    }
                    # Check for confs
                    parent = os.path.dirname(entry.path)
                    name   = entry.name
                    fname  = fs.getFileName(entry.name)
                    # Check for root file entry
                    hardCodedEntries = ["overwrites","options", "nameoverwrite","pathoverwrite","desc","aliases","args","blockCommonParameters","encoding","argparseHelp","synopsisDesc","restrictionMode","readerReturnVars"]
                    ## check for file
                    if parent not in knownRootFiles.keys():
                        for ext in rootFileExts:
                            possibleRoot1 = f"{parent}{os.sep}package.{ext}"
                            possibleRoot2 = f"{parent}{os.sep}cmdlets.{ext}"
                            if os.path.exists(possibleRoot1):
                                # fix for package-root-files (non-cmdlet-configs), they are always package.json. See cslib._crosshellMpackageSystem.getPackageData
                                if allowOldPackageFile == False and ext.lower() == "json":
                                    _tmpContent = _getConfContent(str(possibleRoot1),encoding=encoding)
                                    if _tmpContent.get("cmdlets") != None:
                                        knownRootFiles[parent] = str(possibleRoot1)
                                    elif os.path.exists(possibleRoot2):
                                        knownRootFiles[parent] = str(possibleRoot2)
                                else:
                                    knownRootFiles[parent] = str(possibleRoot1)
                            elif os.path.exists(possibleRoot2):
                                knownRootFiles[parent] = str(possibleRoot2)
                    ## check for entry in root file
                    if parent in knownRootFiles.keys():
                        rootFileContent = _getConfContent(knownRootFiles[parent],encoding=encoding)
                        if rootFileContent.get("cmdlets") != None:
                            rootFileContent = rootFileContent.get("cmdlets")
                        rootEntry = None
                        if name in rootFileContent.keys():
                            rootEntry = rootFileContent.get(name)
                        elif fname in rootFileContent.keys():
                            rootEntry = rootFileContent.get(fname)
                        if rootEntry != None:
                            if rootEntry.get("overwrites") != None:
                                if rootEntry["overwrites"].get("name"):
                                    regEntry["name"] = rootEntry["overwrites"].get("name")
                                if rootEntry["overwrites"].get("path"):
                                    regEntry["path"] = _parseCfgPathTags(
                                        rootEntry["overwrites"].get("path"),
                                        package,
                                        knownRootFiles[parent]
                                    )
                                    if chck_fending != "MIME_EXECUTABLE":
                                        regEntry["fending"] = fs.getFileExtension(regEntry["path"]).lower()
                            if rootEntry.get("desc") != None:
                                regEntry["desc"] = rootEntry.get("desc")
                            if rootEntry.get("description") != None:
                                regEntry["desc"] = rootEntry.get("desc")
                            if rootEntry.get("aliases") != None:
                                if type(rootEntry.get("aliases")) == list:
                                    regEntry["aliases"] = rootEntry.get("aliases")
                            if rootEntry.get("args") != None:
                                regEntry["args"] = rootEntry.get("args")
                            if rootEntry.get("blockCommonParameters") != None:
                                regEntry["blockCommonParameters"] = bool(rootEntry.get("blockCommonParameters"))
                            if rootEntry.get("encoding") != None:
                                regEntry["encoding"] = rootEntry.get("encoding")
                            if rootEntry.get("options") != None:
                                if rootEntry["options"].get("argparseHelp") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    regEntry["options"]["argparseHelp"] = bool(rootEntry["options"].get("argparseHelp"))
                                    if _toBool(regEntry["options"]["argparseHelp"]) == True:
                                        regEntry["args"] = _getArgparseHelp(regEntry["args"],regEntry["path"])
                                if rootEntry["options"].get("synopsisDesc") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    regEntry["options"]["synopsisDesc"] = bool(rootEntry["options"].get("synopsisDesc"))
                                    if _toBool(regEntry["options"]["synopsisDesc"]) == True:
                                        regEntry["desc"] = _getSynopsisDesc(regEntry["desc"],regEntry["path"],regEntry["encoding"])
                                if rootEntry["options"].get("restrictionMode") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    regEntry["options"]["restrictionMode"] = rootEntry["options"].get("restrictionMode")
                                if rootEntry["options"].get("readerReturnVars") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    regEntry["options"]["readerReturnVars"] = bool(rootEntry["options"].get("readerReturnVars"))
                                if rootEntry["options"].get("dontLoad") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    regEntry["options"]["dontLoad"] = bool(rootEntry["options"].get("dontLoad"))
                            for key in rootEntry.keys():
                                if key not in hardCodedEntries:
                                    if "returnCSVars" in str(key):
                                        if regEntry.get("options") == None: regEntry["options"] = {}
                                        regEntry["options"]["readerReturnVars"] = rootEntry[key]
                                    regEntry["extras"][key] = rootEntry[key]
                    # Check for conf file
                    for ext in confFileExts:
                        possibleConf = f"{parent}{os.sep}{fname}.{ext}"
                        if os.path.exists(possibleConf):
                            confFile = str(possibleConf)
                    ## append
                    if confFile != None and os.path.exists(confFile):
                        data = _getConfContent(confFile,encoding)
                        if data.get("description") != None:
                            regEntry["desc"] = data.get("description")
                        if data.get("aliases") != None:
                            regEntry["aliases"] = data.get("aliases")
                        if data.get("paramhelp") != None:
                            regEntry["args"] = data.get("paramhelp")
                        if data.get("blockCommonparams") != None:
                            regEntry["blockCommonParameters"] = bool(data.get("blockCommonparams"))
                        if data.get("ArgparseHelp") != None:
                            if regEntry.get("options") == None: regEntry["options"] = {}
                            if regEntry["options"].get("argparseHelp") != None:
                                regEntry["options"]["argparseHelp"] = bool(data.get("ArgparseHelp"))
                                if _toBool(regEntry["options"]["argparseHelp"]) == True:
                                    regEntry["args"] = _getArgparseHelp(regEntry["args"],regEntry["path"])
                        if data.get("synopsisDesc") != None:
                            if regEntry.get("options") == None: regEntry["options"] = {}
                            if regEntry["options"].get("synopsisDesc") != None:
                                regEntry["options"]["synopsisDesc"] = bool(data.get("synopsisDesc"))
                                if _toBool(regEntry["options"]["synopsisDesc"]) == True:
                                    regEntry["desc"] = _getSynopsisDesc(regEntry["desc"],regEntry["path"],regEntry["encoding"])
                        if data.get("nameoverwrite") != None:
                            regEntry["name"] = data.get("nameoverwrite")
                        if data.get("pathoverwrite") != None:
                            regEntry["path"] = _parseCfgPathTags(
                                data.get("pathoverwrite"),
                                package,
                                confFile
                            )
                            if chck_fending != "MIME_EXECUTABLE":
                                regEntry["fending"] = fs.getFileExtension(regEntry["path"]).lower()
                        if data.get("restrictionMode") != None:
                            if regEntry.get("options") == None: regEntry["options"] = {}
                            if regEntry["options"].get("restrictionMode") != None:
                                regEntry["options"]["restrictionMode"] = data.get("restrictionMode")
                        if data.get("readerReturnVars") != None:
                            if regEntry.get("options") == None: regEntry["options"] = {}
                            if regEntry["options"].get("readerReturnVars") != None:
                                regEntry["options"]["readerReturnVars"] = bool(data.get("readerReturnVars"))
                        if data.get("dontLoad") != None:
                            if regEntry.get("options") == None: regEntry["options"] = {}
                            if regEntry["options"].get("dontLoad") != None:
                                regEntry["options"]["dontLoad"] = bool(data.get("dontLoad"))
                        for key in data.keys():
                            if key not in hardCodedEntries:
                                if "returnCSVars" in str(key):
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    regEntry["options"]["readerReturnVars"] = data[key]
                                regEntry["extras"][key] = data[key]
                    # Check for header-data if enabled in settings
                    if settings.getProperty("crsh","Packages.Options.LoadInFileHeader") == True:
                        # check if file supports this even
                        if is_text_file(entry.path) == True:
                            content = open(entry.path,'r',encoding=regEntry["encoding"]).read()
                            if "\n" in content:
                                lines = content.split("\n")
                            else:
                                lines = [content]
                            if "[CStags]" in content and "[TagEnd]" in content:
                                headFound = False
                                tailFound = False
                                configLines = []
                                for line in lines:
                                    sline = line.strip()
                                    if sline.startswith("#") == True or sline.startswith("::") == True or sline.startswith("//") == True:
                                        if "[CStags]" in sline:
                                            headFound = True
                                        if "[TagEnd]" in sline:
                                            tailFound = True
                                        # Config line
                                        if headFound == True and tailFound != True:
                                            if "[CStags]" not in sline:
                                                sline = sline.replace("#","",1)
                                                sline = sline.replace("::","",1)
                                                sline = sline.replace("//","",1)
                                                sline = sline.strip()
                                                configLines.append(sline)
                                data = config_to_dict("\n".join(configLines).rstrip("\n"))
                                # Get data
                                if data.get("description") != None:
                                    regEntry["desc"] = data.get("description")
                                if data.get("aliases") != None:
                                    regEntry["aliases"] = data.get("aliases")
                                if data.get("paramhelp") != None:
                                    regEntry["args"] = data.get("paramhelp")
                                if data.get("blockCommonparams") != None:
                                    regEntry["blockCommonParameters"] = bool(data.get("blockCommonparams"))
                                if data.get("ArgparseHelp") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    if regEntry["options"].get("argparseHelp") != None:
                                        regEntry["options"]["argparseHelp"] = bool(data.get("ArgparseHelp"))
                                        if _toBool(regEntry["options"]["argparseHelp"]) == True:
                                            regEntry["args"] = _getArgparseHelp(regEntry["args"],regEntry["path"])
                                if data.get("synopsisDesc") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    if regEntry["options"].get("synopsisDesc") != None:
                                        regEntry["options"]["synopsisDesc"] = bool(data.get("synopsisDesc"))
                                        if _toBool(regEntry["options"]["synopsisDesc"]) == True:
                                            regEntry["desc"] = _getSynopsisDesc(regEntry["desc"],regEntry["path"],regEntry["encoding"])
                                if data.get("nameoverwrite") != None:
                                    regEntry["name"] = data.get("nameoverwrite")
                                if data.get("pathoverwrite") != None:
                                    regEntry["path"] = _parseCfgPathTags(
                                        data.get("pathoverwrite"),
                                        package,
                                        entry.path
                                    )
                                    if chck_fending != "MIME_EXECUTABLE":
                                        regEntry["fending"] = fs.getFileExtension(regEntry["path"]).lower()
                                if data.get("restrictionMode") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    if regEntry["options"].get("restrictionMode") != None:
                                        regEntry["options"]["restrictionMode"] = data.get("restrictionMode")
                                if data.get("readerReturnVars") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    if regEntry["options"].get("readerReturnVars") != None:
                                        regEntry["options"]["readerReturnVars"] = bool(data.get("readerReturnVars"))
                                if data.get("dontLoad") != None:
                                    if regEntry.get("options") == None: regEntry["options"] = {}
                                    if regEntry["options"].get("dontLoad") != None:
                                        regEntry["options"]["dontLoad"] = bool(data.get("dontLoad"))
                                for key in data.keys():
                                    if key not in hardCodedEntries:
                                        if str(data[key]).lower() == "true" or str(data[key]).lower() == "false": data[key] = bool(data[key])
                                        if "returnCSVars" in str(key):
                                            if regEntry.get("options") == None: regEntry["options"] = {}
                                            regEntry["options"]["readerReturnVars"] = data[key]
                                        regEntry["extras"][key] = data[key]
                    # Fix duplicates
                    if regEntry["extras"].get("description") != None and regEntry.get("desc") != None:
                        regEntry["extras"].pop("description")
                    if regEntry["extras"].get("paramhelp") != None and regEntry.get("args") != None:
                        regEntry["extras"].pop("paramhelp")
                    if regEntry["extras"].get("blockCommonparams") != None and regEntry.get("blockCommonParameters") != None:
                        regEntry["extras"].pop("blockCommonparams")
                    if regEntry["extras"].get("ArgparseHelp") != None and regEntry["options"].get("argparseHelp") != None:
                        regEntry["extras"].pop("ArgparseHelp")
                    if regEntry["extras"].get("synopsisDesc") != None and regEntry["options"].get("synopsisDesc") != None:
                        regEntry["extras"].pop("synopsisDesc")
                    if regEntry["extras"].get("restrictionMode") != None and regEntry["options"].get("restrictionMode") != None:
                        regEntry["extras"].pop("restrictionMode")
                    if regEntry["extras"].get("readerReturnVars") != None and regEntry["options"].get("readerReturnVars") != None:
                        regEntry["extras"].pop("readerReturnVars")
                    if regEntry["extras"].get("dontLoad") != None and regEntry["options"].get("dontLoad") != None:
                        regEntry["extras"].pop("dontLoad")
                    # Add regEntry to registry
                    if regEntry["options"]["dontLoad"] == False:
                        regEntry_name = str(regEntry["name"])
                        regEntry.pop("name")
                        registry["cmdlets"][ regEntry_name ] = regEntry
    return registry["cmdlets"]