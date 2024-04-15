import os
from cslib.pathtools import normPathSep
from cslib.types import picklePrioCopy, merge_dicts
from cslib.datafiles import _fileHandler,config_to_dict,rudaDotfile_to_dict
from cslib._crosshellMpackageSystem import toLeastInfoStr

from cslib.execution import input_to_pipelineStructure,execline
from cslib.externalLibs.conUtils import clear,setConTitle
from cslib.exceptions import CrosshellDebErr

# region: [FeatureManglers]
def componentMangler(data=dict,pkgConfigs=dict,componentFolder=str) -> dict:
    for packageType,componentIncludingPkg in data.items():
        for package,componentD in componentIncludingPkg.items():
            try:
                pathableName = os.path.basename(pkgConfigs[packageType][package]["path"])
            except KeyError:
                pathableName = package
            for componentName,componentData in componentD.items():
                if componentData.get("file") != None:
                    rootPath = os.path.join( ("{CS_lPackPath}" if packageType == "legacy" else "{CS_mPackPath}"), pathableName ) + componentFolder
                    file = componentData["file"]
                    if file.startswith("{parent}"):
                        file = file.replace("{parent}",rootPath)
                    else:
                        file = file.replace("\\","/")
                        if file.startswith("./"):
                            file = rootPath + file.lstrip(".")
                    file = file.replace("\\","/")
                    data[packageType][package][componentName]["file"] = file
    return data

def readerMangler(data=dict,pkgConfigs=dict,readerFolder=str,addMethod=None,readerFile=None,readerFileEncoding="utf-8",readerFileIsStream=False) -> dict:
    # Add the readers to the readerFile
    for packageType,readerIncludingPkg in data.items():
        for package,readerD in readerIncludingPkg.items():
            try:
                pathableName = os.path.basename(pkgConfigs[packageType][package]["path"])
            except KeyError:
                pathableName = package
            for reader in readerD.keys():
                if package.lower() != "builtins":
                    if packageType == "legacy": rootPath = "{CS_lPackPath}"
                    else: rootPath = "{CS_mPackPath}"
                    readerBase = rootPath + os.sep + pathableName + os.sep + readerFolder + os.sep + reader
                    readerPath = readerBase + ".py"
                    readerName = os.path.splitext(os.path.basename(readerPath))[0]
                    addMethod(readerName,readerPath,readerFile,encoding=readerFileEncoding,isStream=readerFileIsStream)
    return data

def langpckMangler(data=dict,pkgConfigs=dict,lngPackFolder=str,languageProvider=None,languagePath=None,mPackPath=str) -> dict:
    languageFiles = []
    for pkgType,x in data.items():
        for package,y in x.items():
            try:
                pathableName = os.path.basename(pkgConfigs[pkgType][package]["path"])
            except KeyError:
                pathableName = package
            for z in y.values():
                for file in z:
                    if mPackPath.endswith("."):
                        mPackPath = (mPackPath[::-1].replace(".","",1))[::-1]
                    fpath = mPackPath + "/" + pathableName + lngPackFolder + os.sep + file
                    fpath = normPathSep(fpath)
                    languageFiles.append( fpath )
    if languageProvider != None and languagePath != None:
        for file in languageFiles:
            if os.path.exists(file):
                fpath = os.path.dirname(file)
                languagePath.append(fpath)
                languageProvider.populateList()
    return {"langfiles":languageFiles}

def cmdletMangler(data=dict,pkgConfigs=dict,lPackPath=str,mPackPath=str,cmdletStdEncoding=str,cmdletSchema=dict,allowedPackageConfigTypes=["json"],allowedCmdletConfigTypes=["cfg","config"],enableParsingOfRudamentaryDotFiles=False,dotFileEncoding="utf-8") -> dict:
    rearrangedData = {}
    knowBase_duplicateAmnt = {}
    knowBase_duplicateAmnt_sn = {}
    index = 0
    # Allowed keys (keys that won't map into extras)
    sumAllowedKeys = ["pathoverwrite","nameoverwrite","idoverwrite","override_path","override_name","override_id"]
    # More keys that won't mapp but theese only apply to dotfile or configfile
    sumAllowedKeys2 = ["description","aliases","paramhelp"]
    # Keys that don't mapp to extras but will be mapped (adding a key here will remove any None valued)
    tidyThis_None = []
    tidyThis_None.extend(sumAllowedKeys)
    # Same as above but removed no-matter None or not
    tidyThis_Alw = ["paramhelp","description"]
    # Get data:
    for pkgType,x in data.items():
        for pkg,y in x.items():
            # Get pkgpath
            pkgPath = None
            if pkgType == "legacy": pkgPath = lPackPath
            if pkgType == "modulo": pkgPath = mPackPath
            pkgPath_s = normPathSep(pkgPath)
            if pkgPath_s.endswith(os.sep):
                pkgPath_s = (pkgPath_s[::-1].replace(os.sep,"",1))[::-1]
            # Add data
            for reader,cmdlets in y.items():
                for cmdlet in cmdlets:
                    # cmdletName
                    cmdletName = os.path.splitext(os.path.basename(cmdlet))[0]
                    # ID
                    generatedID = pkgType +":"+ pkg +"/"+ cmdletName
                    if generatedID not in knowBase_duplicateAmnt.keys():
                        knowBase_duplicateAmnt[generatedID] = 1
                    else:
                        knowBase_duplicateAmnt[generatedID] += 1
                    generatedID_final = generatedID + "#" + str(knowBase_duplicateAmnt[generatedID])
                    # Shortname
                    shortname = toLeastInfoStr(generatedID_final,list(rearrangedData.keys()))
                    if shortname not in knowBase_duplicateAmnt_sn.keys():
                        knowBase_duplicateAmnt_sn[shortname] = 1
                        shortname_final = shortname
                    else:
                        knowBase_duplicateAmnt_sn[shortname] += 1
                        shortname_final = shortname + "#" + str(knowBase_duplicateAmnt_sn[shortname])
                    # CmdletPath
                    cmdletPath_s = normPathSep(cmdlet)
                    if not cmdletPath_s.startswith(os.sep):
                        cmdletPath_s = cmdletPath_s.replace(os.sep,"",1)
                    cmdletPath = pkgPath_s + os.sep+pkg + cmdletPath_s
                    # Set Data
                    rearrangedData[generatedID_final] = picklePrioCopy(cmdletSchema)
                    rearrangedData[generatedID_final].update({
                        "type": "file",
                        "name": cmdletName,
                        "fending": os.path.splitext(cmdletPath)[1].replace(".","",1),
                        "filename": os.path.basename(cmdlet),
                        "method": None,
                        "reader": reader,
                        "path": cmdletPath,
                        "parentPackage": {
                            "name": pkg,
                            "shortname": shortname_final,
                            "type": pkgType,
                            "rootPath": normPathSep(pkgPath + os.sep+pkg)
                        },
                        "dupeID": knowBase_duplicateAmnt[generatedID],
                        "index": index
                    })
                    rearrangedData[generatedID_final]["data"]["encoding"] = cmdletStdEncoding
                    # Increment index
                    index += 1
    # Clean up
    del knowBase_duplicateAmnt
    # Load cmdletdata from configs
    ## load from package.json
    for gid,data1 in rearrangedData.items():
        # Find possible
        packageJsonFilePath = None
        packageJsonFileType = None
        for type_ in allowedPackageConfigTypes:
            possiblePackageJsonFilePath = os.path.join(data1["parentPackage"]["rootPath"],"package."+type_)
            if os.path.exists(possiblePackageJsonFilePath):
                packageJsonFilePath = possiblePackageJsonFilePath
                packageJsonFileType = type_
        mode = "modulo.new"
        switch_loadConfigs = True
        switch_loadDotFiles = enableParsingOfRudamentaryDotFiles
        # If found load it under the cmdlets key
        if packageJsonFilePath != None and packageJsonFileType != None:
            # Get
            raw = _fileHandler(packageJsonFileType,"get",packageJsonFilePath)
            # Compat
            compatability = raw.get("compat")
            if compatability != None:
                if compatability.get("cmdlets:use_old_modulo_schema") == True:
                    mode = "modulo.old"
                elif compatability.get("cmdlets:use_raw_loading") == True:
                    mode = "raw"
            # Switches
            switching = raw.get("loaderOptions")
            if switching != None:
                dis_cfg = switching.get("cmdlets:disableConfigFileLoad")
                dis_dot = switching.get("cmdlets:disableDotFileLoad")
                if type(dis_cfg) == bool:
                    switch_loadConfigs = not dis_cfg
                if type(dis_dot) == bool:
                    switch_loadDotFiles = not dis_dot
            # Cmdlets
            cmdlets = raw.get("cmdlets")
            filename_d = os.path.splitext(data1["filename"])[0]
            if cmdlets != None and cmdlets.get(filename_d) != None:
                # Prep extras
                extras = {}
                allowed_keys = list(rearrangedData[gid]["data"].keys())
                allowed_keys.extend(sumAllowedKeys)
                for k,v in cmdlets[filename_d].items():
                    if k not in allowed_keys:
                        extras[k] = v
                        del cmdlets[filename_d][k]
                # Mode: Raw
                if mode == "raw":
                    rearrangedData[gid] = merge_dicts(rearrangedData[gid],cmdlets[filename_d])
                # Mode: modulo.old
                elif mode == "modulo.old":
                    rearrangedData[gid]["data"] = merge_dicts(rearrangedData[gid]["data"],cmdlets[filename_d])
                    # fix
                    rearrangedData[gid]["data"]["Options"]["blockCommonParams"] = rearrangedData[gid]["data"]["blockCommonparams"]
                    del rearrangedData[gid]["data"]["blockCommonparams"]
                # Mode: modulo.new
                else:
                    rearrangedData[gid]["data"] = merge_dicts(rearrangedData[gid]["data"],cmdlets[filename_d])
                rearrangedData[gid]["data"]["extras"].update(extras)
                rearrangedData[gid]["readAs"] = mode
        ## load from <cmdlet_filename>.<allowedConfigFileType>, fix so extra tags that are under options in schema gets placed under options, also handle extra tags
        basePathname = os.path.join(os.path.dirname(rearrangedData[gid]["path"]),os.path.splitext(rearrangedData[gid]["filename"])[0])
        if switch_loadConfigs == True:
            for type_ in allowedCmdletConfigTypes:
                possibleCmdletConfigFilePath = basePathname + "." + type_
                if os.path.exists(possibleCmdletConfigFilePath):
                    conf_data = config_to_dict(open(possibleCmdletConfigFilePath,'r').read())
                    extras = {}
                    newData = {}
                    currentKeys = list(conf_data.keys())
                    for k in currentKeys:
                        v = conf_data[k]
                        allowed_keys = list(rearrangedData[gid]["data"].keys())
                        allowed_keys.extend(sumAllowedKeys)
                        allowed_keys.extend(sumAllowedKeys2)
                        if k == "blockCommonparams":
                            if type(newData.get("options")) != dict: newData["Options"] = {}
                            newData["Options"]["blockCommonParams"] = v
                            del conf_data[k]
                        elif k not in allowed_keys:
                            extras[k] = v
                            del conf_data[k]
                        else:
                            newData[k] = v
                    newData["extras"] = extras
                    # Map
                    if conf_data.get("description") != None:
                        newData["desc"] = conf_data["description"]
                    if conf_data.get("aliases") != None:
                        newData["aliases"] = conf_data["aliases"]
                    if conf_data.get("paramhelp") != None:
                        newData["args"] = conf_data["paramhelp"]
                    rearrangedData[gid]["data"].update(newData)
        ## load from .<cmdlet_filename> (if "rudamentary-dotfiles" are enabled), fix so extra tags that are under options in schema gets placed under options, also handle extra tags
        if enableParsingOfRudamentaryDotFiles == True and switch_loadDotFiles == True:
            basePathname = os.path.dirname(rearrangedData[gid]["path"])
            possibleCmdletDotfileFilePath = os.path.join(basePathname,"."+os.path.splitext(rearrangedData[gid]["filename"])[0])
            if os.path.exists(possibleCmdletDotfileFilePath):
                rudaData = rudaDotfile_to_dict(open(possibleCmdletDotfileFilePath,'r',encoding=dotFileEncoding).read())
                selSection = "Default"
                if rudaData.get("Cmdlet") != None: selSection = "Cmdlet"
                # set
                newData = rudaData.get(selSection)
                del rudaData[selSection]
                # Mapping
                if newData.get("Override") != None:
                    # Override:path
                    if newData["Override"].get("path") != None:
                        if mode == "modulo.old":
                            newData["pathoverwrite"] = newData["Override"]["path"]
                        else:
                            newData["override_path"] = newData["Override"]["path"]
                        del newData["Override"]["path"]
                    # Override:name
                    if newData["Override"].get("name") != None:
                        if mode == "modulo.old":
                            newData["nameoverwrite"] = newData["Override"]["name"]
                        else:
                            newData["override_name"] = newData["Override"]["name"]
                        del newData["Override"]["name"]
                    # Override:id
                    if newData["Override"].get("id") != None:
                        if mode == "modulo.old":
                            newData["idoverwrite"] = newData["Override"]["id"]
                        else:
                            newData["override_id"] = newData["Override"]["id"]
                        del newData["Override"]["id"]
                newData_ = {}
                for nsp,nspd in newData.items():
                    if nspd != {}:
                        newData_[nsp] = nspd
                newData = newData_
                if newData.get("Default") != None:
                    newData.update(newData["Default"])
                    del newData["Default"]
                extras = {}
                newData2 = {}
                currentKeys = list(newData.keys())
                for k in currentKeys:
                    v = newData[k]
                    allowed_keys = list(rearrangedData[gid]["data"].keys())
                    allowed_keys.extend(sumAllowedKeys)
                    allowed_keys.extend(sumAllowedKeys2)
                    if k == "blockCommonparams":
                        if type(newData2.get("options")) != dict: newData2["Options"] = {}
                        newData2["Options"]["blockCommonParams"] = v
                        del newData[k]
                    elif k not in allowed_keys:
                        extras[k] = v
                        del newData[k]
                    else:
                        newData2[k] = v
                newData2["extras"] = extras
                newData2["dotFileRaw"] = rudaData
                rearrangedData[gid]["data"].update(newData2)
                del newData,extras,currentKeys,newData2
        ## Fix invalid strings, and replace paths with placeholders
        if type(rearrangedData[gid]["data"]["desc"]) != dict:
            rearrangedData[gid]["data"]["desc"] = {
                "type": "raw",
                "content": rearrangedData[gid]["data"]["desc"]
            }
        v = rearrangedData[gid]["data"]["args"]
        if type(rearrangedData[gid]["data"]["args"]) != dict:
            rearrangedData[gid]["data"]["args"] = {}
            for arg in v.split(" "):
                rearrangedData[gid]["data"]["args"][arg] = {
                    "type": "raw",
                    "content": ""
                }
        else:
            for k,v in rearrangedData[gid]["data"]["args"].items():
                if type(v) != dict:
                    rearrangedData[gid]["data"]["args"][k] = {
                        "type": "raw",
                        "content": v
                    }
        # Fix path/name/id placeholders
        if mode == "modulo.old":
            v = rearrangedData[gid]["data"].get("pathoverwrite")
            if v != None and v != "" and type(v) == str:
                rearrangedData[gid]["path"] = rearrangedData[gid]["data"]["pathoverwrite"]
                rearrangedData[gid]["data"]["hasOverriddenWith"]["path"] = rearrangedData[gid]["data"]["pathoverwrite"]
                del rearrangedData[gid]["data"]["pathoverwrite"]
            v = rearrangedData[gid]["data"].get("nameoverwrite")
            if v != None and v != "" and type(v) == str:
                rearrangedData[gid]["name"] = rearrangedData[gid]["data"]["nameoverwrite"]
                rearrangedData[gid]["data"]["hasOverriddenWith"]["name"] = rearrangedData[gid]["data"]["nameoverwrite"]
                del rearrangedData[gid]["data"]["nameoverwrite"]
            v = rearrangedData[gid]["data"].get("idoverwrite")
            if v != None and v != "" and type(v) == str:
                rearrangedData[gid] = rearrangedData[rearrangedData[gid]["data"]["idoverwrite"]]
                rearrangedData[gid]["data"]["hasOverriddenWith"]["id"] = rearrangedData[gid]["data"]["idoverwrite"]
                del rearrangedData[gid]["data"]["idoverwrite"]
        else:
            v = rearrangedData[gid]["data"].get("override_path")
            if v != None and v != "" and type(v) == str:
                rearrangedData[gid]["path"] = rearrangedData[gid]["data"]["override_path"]
                rearrangedData[gid]["data"]["hasOverriddenWith"]["path"] = rearrangedData[gid]["data"]["override_path"]
                del rearrangedData[gid]["data"]["override_path"]
            v = rearrangedData[gid]["data"].get("override_name")
            if v != None and v != "" and type(v) == str:
                rearrangedData[gid]["name"] = rearrangedData[gid]["data"]["override_name"]
                rearrangedData[gid]["data"]["hasOverriddenWith"]["name"] = rearrangedData[gid]["data"]["override_name"]
                del rearrangedData[gid]["data"]["override_name"]
            v = rearrangedData[gid]["data"].get("override_id")
            if v != None and v != "" and type(v) == str:
                rearrangedData[gid] = rearrangedData[rearrangedData[gid]["data"]["override_id"]]
                rearrangedData[gid]["data"]["hasOverriddenWith"]["id"] = rearrangedData[gid]["data"]["override_id"]
                del rearrangedData[gid]["data"]["override_id"]
        # Tidy
        for key in tidyThis_None:
            if key in rearrangedData[gid]["data"] and rearrangedData[gid]["data"][key] == None:
                del rearrangedData[gid]["data"][key]
        for key in tidyThis_Alw:
            if key in rearrangedData[gid]["data"]:
                del rearrangedData[gid]["data"][key]
    ## return
    return rearrangedData

def dynprefixMangler(data=dict,pkgConfigs=dict,dynprefixFolder=str) -> dict:
    dynPrefixes = {}
    for pkgType,x in data.items():
        for pkgName,dynPrefixData in x.items():
            try:
                pathableName = os.path.basename(pkgConfigs[pkgType][pkgName]["path"])
            except KeyError:
                pathableName = pkgName
            for key, path in dynPrefixData.items():
                rootPath = normPathSep(pkgConfigs[pkgType][pkgName]["path"] + dynprefixFolder)
                if path.startswith("{parent}"):
                    path = path.replace("{parent}",rootPath)
                else:
                    path = path.replace("\\","/")
                    if path.startswith("./"):
                        path = rootPath + path.lstrip(".")
                path = path.replace("\\","/")
                dynPrefixes[pathableName+":"+key] = path
    return dynPrefixes

# endregion

# region: [Components]
def console_component(csSession):

    # Create a persistant pipeline to not have to recreate it on each prompt
    _pipeline = execline()

    # Get settings obj
    _set = csSession.getregister("set")

    # Prep console
    if _set.getProperty("crsh","Console.ClearOnStart") == True:
        clear(skipSetXY=True)
    if _set.getProperty("crsh","Console.TitleEnabled") == True:
        setConTitle( csSession.getTitle() )

    # Get prefix
    if _set.getProperty("crsh","Console.PrefixEnabled") == True:
        prefix = csSession.getPrefix()
    else:
        prefix = ""

    # Define "running" state
    csSession.flags.enable("--consoleRunning")

    # Loop and prompt
    ret = None
    try:
        while csSession.flags.has("--consoleRunning"):
            ret = csSession.eprompt(prefix,_pipeline=_pipeline)
            if ret != None: print(ret)
    except KeyboardInterrupt:
        print("\n[Crosshell]: Ended by keyboard interrupt. Bya <3")
    del _set
    return ret

def interpriter_component(csSession,input_=str,_pipeline=None) -> object:
    # Ensure a execline obj
    if _pipeline == None:
        pipeline = execline()
    else:
        pipeline = _pipeline

    # Get it into a basic pipeline-structure
    pipelineStructure = input_to_pipelineStructure(input_,basicExecutionDelimiters=["||",";"])
    # Retrive the path/method to exec
    for segI,segment in enumerate(pipelineStructure):
        for parI,partial in enumerate(segment):
            if partial["cmd"].strip() != "":
                for cmdletID,cmdletData in csSession.regionalGet("LoadedPackageData")["cmdlets"]["data"].items():
                    cmdAliases = cmdletData["data"].get("aliases")
                    if cmdAliases == None: cmdAliases = []
                    if partial["cmd"] == cmdletData["name"] or partial["cmd"] in cmdAliases: #TODO: assuming string aliases might not be the best
                        pipelineStructure[segI][parI]["cmd"] = cmdletData
                        pipelineStructure[segI][parI]["handle"] = "valid"
                        break
                else:
                    pipelineStructure[segI][parI]["handle"] = "invalid"
            else:
                pipelineStructure[segI][parI]["handle"] = "ignore"
    pipeline.setSegments(pipelineStructure)
    return pipeline

def execute_component(csSession,execline=object) -> object:
    try:
        return execline.execute(csSession)
    except CrosshellDebErr as e:
        return e

def prompt_component(csSession,prompt=str) -> str:
    return input(prompt)
# endregion

# region: [Cmdlets]
def methodCmdet_exit(globalData):
    csSession = globalData["csSession"]
    if csSession.flags.has("--consoleRunning"):
        csSession.flags.disable("--consoleRunning")
    exit(0)

def methodCmdet_print(globalData):
    print(globalData["args"].sargv)
# endregion

# region: [PassableMethods]
def dynprefix_include_constructor(csSession,dynPrefixFile,allow,fromPath):
    def dynprefix_include(filename=str):
        if "\\"  in filename or "/" in filename or "." in filename:
            csSession.deb.perror("lng:cs.prefixsys.dynprefix.invalidinclude",{"dynPrefixFile":dynPrefixFile})
        if allow == True:
            filename += ".py"
            return fromPath(os.path.join(os.path.dirname(dynPrefixFile),filename))
    return dynprefix_include

# endregion
