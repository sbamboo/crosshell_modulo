import os
from cslib.pathtools import normPathSep
from cslib.types import picklePrioCopy, merge_dicts
from cslib.datafiles import _fileHandler,config_to_dict
from cslib._crosshellMpackageSystem import idToDict, toLeastInfoStr

# FeatureManglers
def readerMangler(data=dict,addMethod=None,readerFile=None,readerFileEncoding="utf-8",readerFileIsStream=False) -> dict:
    # Add the readers to the readerFile
    readers = {}
    for packageType,readerIncludingPkg in data.items():
        for package,readerD in readerIncludingPkg.items():
            for reader in readerD.keys():
                if package.lower() != "builtins":
                    if packageType == "legacy": rootPath = "{CS_lPackPath}"
                    else: rootPath = "{CS_mPackPath}"
                    readerBase = os.path.join(rootPath,package,reader)
                    readerPath = readerBase + ".py"
                    readerName = os.path.splitext(os.path.basename(readerPath))[0]
                    addMethod(readerName,readerPath,readerFile,encoding=readerFileEncoding,isStream=readerFileIsStream)
    return data

def langpckMangler(data=dict,languageProvider=None,languagePath=None,mPackPath=str) -> dict:
    languageFiles = []
    for x in data.values():
        for package,y in x.items():
            for z in y.values():
                for file in z:
                    if mPackPath.endswith("."):
                        mPackPath = (mPackPath[::-1].replace(".","",1))[::-1]
                    fpath = mPackPath + "/" + package + "/Langpck/" + file
                    fpath = normPathSep(fpath)
                    languageFiles.append( fpath )
    if languageProvider != None and languagePath != None:
        for file in languageFiles:
            if os.path.exists(file):
                languagePath.append(os.path.dirname(file))
                languageProvider.populateList()
    return {"langfiles":languageFiles}

def cmdletMangler(data=dict,lPackPath=str,mPackPath=str,cmdletStdEncoding=str,cmdletSchema=dict,allowedPackageConfigTypes=["json"],allowedCmdletConfigTypes=["cfg","config"]) -> dict:
    rearrangedData = {}
    knowBase_duplicateAmnt = {}
    knowBase_duplicateAmnt_sn = {}
    index = 0
    sumAllowedKeys = ["pathoverwrite","nameoverwrite","idoverwrite","override_path","override_name","override_id"]
    sumAllowedKeys2 = ["description","aliases","paramhelp"]
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
                        "name": cmdletName,
                        "fending": os.path.splitext(cmdletPath)[1].replace(".","",1),
                        "filename": os.path.basename(cmdlet),
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
        # If found load it under the cmdlets key
        if packageJsonFilePath != None and packageJsonFileType != None:
            raw = _fileHandler(packageJsonFileType,"get",packageJsonFilePath)
            compatability = raw.get("compat")
            if compatability != None:
                if compatability.get("cmdlets:use_old_modulo_schema") == True:
                    mode = "modulo.old"
                elif compatability.get("cmdlets:use_raw_loading") == True:
                    mode = "raw"
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
        # TODO:^
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
    ## return
    return rearrangedData