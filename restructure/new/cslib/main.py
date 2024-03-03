import pickle, sys, json, os, argparse, inspect, re

from cslib.piptools import installPipDeps_fl
from cslib._crosshellParsingEngine import tagSubstitionManager, pathTagManager, collectionalTagManager, exclude_nonToFormat, include_nonToFormat
from cslib._crosshellGlobalTextSystem import standardHexPalette,crosshellGlobalTextSystem
from cslib.externalLibs.filesys import filesys
from cslib.datafiles import _fileHandler,setKeyPath,getKeyPath
from cslib.exportImport_tools import argParse_to_dict,argParse_from_dict
from cslib.pathtools import normPathSep,normPathSepObj,absPathSepObj
from cslib.progressMsg import startupMessagingWProgress
from cslib.exceptions import CrosshellDebErr

class modularSettingsLinker():
    '''CSlib: Links to a settings file to provide a module system'''
    def __init__(self,settingsFile,encoding="utf-8",ensure=False,readerMode="Comments",discardNewlines=False):
        self.file = settingsFile
        self.modules = []
        self.encoding = encoding
        if ".yaml" in self.file:
            self.filetype = "yaml"
        elif ".json" in self.file or ".jsonc" in self.file or ".json5" in self.file:
            self.filetype = "json"
        if ensure == True:
            if os.path.exists(self.file) != True:
                toc = ""
                if self.filetype == "json":
                    toc = "{}"
                open(self.file,'w',encoding=encoding).write(toc)
        self.readerMode = readerMode
        self.discardNewlines = discardNewlines
        self.keptComments = None
        if os.path.exists(self.file) == False: open(self.file,'x').write("")
    def _getContent(self,_ovFile=None,_ovEnc=None) -> dict:
        toUse = _ovFile if _ovFile != None else self.file
        encoding = _ovEnc if _ovEnc != None else self.encoding
        data = {}
        if self.readerMode.lower() != "off":
            data,self.keptComments = _fileHandler(self.filetype,"get",toUse,encoding=encoding,readerMode=self.readerMode,discardNewlines=self.discardNewlines)
        else:
            data = _fileHandler(self.filetype,"get",toUse,encoding=encoding,readerMode=self.readerMode)
        if data == None: data = {}
        return data
    def _setContent(self,content,_ovFile=None,_ovEnc=None) -> None:
        toUse = _ovFile if _ovFile != None else self.file
        encoding = _ovEnc if _ovEnc != None else self.encoding
        if self.readerMode.lower() != "off":
            _fileHandler(self.filetype,"set",toUse,content,encoding=encoding,readerMode=self.readerMode,discardNewlines=self.discardNewlines,commentsToInclude=self.keptComments)
        else:
            _fileHandler(self.filetype,"set",toUse,content,encoding=encoding,readerMode=self.readerMode)
    def _appendFromFile(self,filepath,_ovEnc=None) -> None:
        """Obs! This function will overwrite any data with the new one, be carefull!"""
        encoding = _ovEnc if _ovEnc != None else self.encoding
        contentRaw = self._getContent(_ovFile=filepath,_ovEnc=self.encoding)
        self._setContent(contentRaw,_ovFile=self.file,_ovEnc=encoding)
    def _appendContent(self,content) -> None:
        if self.filetype == "yaml":
            data = self._getContent()
            if data == None: data = {}
            data.update(content)
            self._setContent(data)
    def _getModules(self) -> list:
        return list(self._getContent().items())
    def createFile(self,overwrite=False):
        self.keptComments = None
        filesys.ensureDirPath(os.path.dirname(self.file))
        if overwrite == True:
            if filesys.doesExist(self.file): filesys.deleteFile(self.file)
            filesys.createFile(self.file)
        else:
            if filesys.notExist(self.file):
                filesys.createFile(self.file)
        if self.filetype == "json":
            content = filesys.readFromFile(self.file)
            if content == "" or content == None:
                filesys.writeToFile("{}")
    def removeFile(self):
        self.keptComments = None
        filesys.deleteFile(self.file)
    def addModule(self,module,overwrite=False) -> None:
        self.modules.append(module)
        data = self._getContent()
        if overwrite == True:
            data[module] = {}
        else:
            if data.get(module) == None:
                data[module] = {}
        self._setContent(data)
    def getModule(self,module) -> None:
        data = self._getContent()
        return data[module]
    def remModule(self,module) -> None:
        if module in self.modules:
            i = self.modules.index(module)
            self.modules.pop(i)
        data = self._getContent()
        if data.get(module) != None:
            data.pop(module)
        self._setContent(data)
    def set(self,module,content,autocreate=False) -> None:
        if module in self.modules:
            data = self._getContent()
            data[module] = content
            self._setContent(data)
        elif autocreate == True:
            self.addModule(module)
            data = self._getContent()
            data[module] = content
            self._setContent(data)
    def rem(self,module,autocreate=False) -> None:
        if module in self.modules:
            data = self._getContent()
            data.pop(module)
            self._setContent(data)
        elif autocreate == True:
            self.addModule(module)
            data = self._getContent()
            data.pop(module)
            self._setContent(data)
    def get(self,module,autocreate=False) -> dict:
        if module in self.modules:
            data = self._getContent()
            return data[module]
        elif autocreate == True:
            self.addModule(module)
            data = self._getContent()
            return data[module]
        else:
            return None
    def update(self,module,content,autocreate=False) -> None:
        if module in self.modules:
            data = self._getContent()
            data[module].update(content)
            self._setContent(data)
        elif autocreate == True:
            self.addModule(module)
            self.set(module,content)
    def addProperty(self,module,keyPath,default,autocreate=False) -> None:
        data = self.get(module,autocreate=autocreate)
        data = setKeyPath(data,keyPath,default)
        self.set(module,data,autocreate=autocreate)
    def getProperty(self,module,keyPath,autocreate=False):
        data = self.get(module,autocreate=autocreate)
        return getKeyPath(data,keyPath)
    def chnProperty(self,module,keyPath,default,autocreate=False) -> None:
        data = self.get(module,autocreate=autocreate)
        data = setKeyPath(data,keyPath,default,nonAppend=True)
        self.set(module,data,autocreate=autocreate)
    def uppProperty(self,module,keyPath,default,autocreate=False) -> None:
        data = self.get(module,autocreate=autocreate)
        data = setKeyPath(data,keyPath,default,update=True)
        self.set(module,data,autocreate=autocreate)
    def remProperty(self,module,keyPath,autocreate=False) -> None:
        data = self.get(module,autocreate=autocreate)
        data = remKeyPath(data,keyPath)
        self.set(module,data,autocreate=autocreate)

def recursiveMultipleReplacementTagWrapper(obj,tags=dict):
    """CSlib: Evals an object in multiple replacementTagWrappers."""
    if type(obj) == dict:
        for k,v in obj.items():
            obj[k] = recursiveMultipleTagWrapper(v,tags)
    elif type(obj) == list or type(obj) == tuple:
        for i,v in enumerate(obj):
            obj[i] = recursiveMultipleTagWrapper(v,tags)
    elif type(obj) == str:
        for tag,tagVal in tags.items():
            if obj == "{"+tag+"}":
                obj = tagVal
    return obj

def ingestDefaults(defaultsFile,encoding="utf-8",instanceMapping=dict):
    defaults = json.loads(open(defaultsFile,'r',encoding=encoding).read())
    for file in defaults.keys():
        if instanceMapping.get(file) != None:
            for module, settings in defaults[file].items():
                instanceMapping[file]["instance"].addModule(module)
                _temp = instanceMapping[file]["instance"].getModule(module)
                for settK,settV in settings.items():
                    if type(settV) == str and settV.startswith("@") and settV.count(":") == 2:
                        split = settV.replace("@","",1).split(":")
                        file2 = split[0]
                        module2 = split[1]
                        settK2 = split[2]
                        if instanceMapping.get(file2) != None:
                            if instanceMapping[file2]["instance"].get(module2) != None:
                                #settV2 = instanceMapping[file2]["instance"].getProperty(module2,settK2)
                                settV2 = getKeyPath(_temp,settK2)
                                settV2 = recursiveMultipleReplacementTagWrapper(settV2,instanceMapping[file]["tags"])
                                #instanceMapping[file]["instance"].addProperty(module,settK,settV2)
                                _temp = setKeyPath(_temp, settK, settV2)
                    else:
                        settV = recursiveMultipleReplacementTagWrapper(settV,instanceMapping[file]["tags"])
                        #instanceMapping[file]["instance"].addProperty(module,settK,settV)
                        _temp = setKeyPath(_temp, settK, settV)
                instanceMapping[file]["instance"].set(module,_temp)
def ingestDefaults_fd(defaults=dict,instanceMapping=dict):
    for file in defaults.keys():
        if instanceMapping.get(file) != None:
            for module, settings in defaults[file].items():
                instanceMapping[file]["instance"].addModule(module)
                _temp = instanceMapping[file]["instance"].getModule(module)
                for settK,settV in settings.items():
                    if type(settV) == str and settV.startswith("@") and settV.count(":") == 2:
                        split = settV.replace("@","",1).split(":")
                        file2 = split[0]
                        module2 = split[1]
                        settK2 = split[2]
                        if instanceMapping.get(file2) != None:
                            if instanceMapping[file2]["instance"].get(module2) != None:
                                settV2 = instanceMapping[file2]["instance"].getProperty(module2,settK2)
                                settV2 = recursiveMultipleReplacementTagWrapper(settV2,instanceMapping[file]["tags"])
                                #instanceMapping[file]["instance"].addProperty(module,settK,settV2)
                                _temp = setKeyPath(_temp, settK, settV2)
                    else:
                        settV = recursiveMultipleReplacementTagWrapper(settV,instanceMapping[file]["tags"])
                        #instanceMapping[file]["instance"].addProperty(module,settK,settV)
                        _temp = setKeyPath(_temp, settK, settV)
                instanceMapping[file]["instance"].set(module,_temp)

def prefixAnyTags(string_with_tags,prefix):
    pattern = r'\{(.*?)\}'
    matches = re.findall(pattern, string_with_tags)
    for m in matches:
        string_with_tags = string_with_tags.replace("{"+m+"}","{"+prefix+m+"}")
    return string_with_tags

def deep_merge_dict_only(dict1, dict2):
    """
    Merge two dictionaries deeply.
    """
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

def _returnPrio(orderdItems,items):
    '''CSlib: Function to return prio list given alternatives and items.'''
    # split to includes and excludes
    includes = []
    excludes = []
    for item in items:
        if not item.startswith("!"):
            includes.append(item)
        else:
            excludes.append(item.replace("!",""))
    # create prio list
    prio = []
    for item in includes:
        if item in orderdItems:
            if item not in excludes:
                index = orderdItems.index(item)
                prio.extend(orderdItems[:index+1])
    # return 
    return prio

def listItemInList(sublist,toplist):
    found = False
    for item in sublist:
        if item in toplist:
            found = True
            break
    return found

def crosshellVersionManager_getData(versionFile,formatVersion="1",encoding="utf-8"):
    '''CSlib: gets the versionData from a compatible version file.'''
    data = {}
    if ".yaml" in versionFile:
        data = _fileHandler("yaml","get",versionFile,encoding=encoding)
    elif ".json" in versionFile or ".jsonc" in versionFile:
        data = _fileHandler("yaml","get",versionFile,encoding=encoding)
    forData = data.get("CSverFile")
    verData = data
    if verData.get("CSverFile") != None: verData.pop("CSverFile")
    if int(forData.get("format")) != int(formatVersion):
        raise Exception(f"Invalid format on versionfile, internal '{formatVersion}' whilst external is '{forData.get('format')}'")
    return verData

class sessionStorage():
    def __init__(self,regionalPrefix=""):
        self.regionalPrefix = regionalPrefix
        self.storage = {
            "tempData": {},
            "userVars": {},
            "regionalScope": {}
        }
    # region: sessionStorage.mainmethods
    def reset(self, key=None):
        if key == None:
            self.storage = {
                "tempData": {},
                "userVars": {},
                "regionalScope": {}
            }
        else:
            self.storage[key] = {}
    def __setitem__(self, key, value):
        self.storage[key] = value
    def __getitem__(self, key):
        return self.storage[key]
    def remove(self, key):
        del self.storage[key]
    def update(self, newDict):
        self.storage.update(newDict)
        return self.storage
    # endregion
    
    # region sessionStorage.regionalmethods
    def regionalSet(self, key, value):
        self.storage["regionalScope"][key] = value
    def regionalGet(self, key=None):
        if key == None:
            return self.storage["regionalScope"]
        else:
            return self.storage["regionalScope"][key]
    def regionalRemove(self, key):
        del self.storage["regionalScope"][key]
    def regionalUpdate(self, newDict):
        self.storage["regionalScope"].update(newDict)
        return self.storage["regionalScope"]
    def regionalReset(self):
        self.storage["regionalScope"] = {}
    def addPrefToKey(self,key):
        if key.strip().startswith("*"):
            key = key.replace("*","",1)
        else:
            key = self.regionalExport + key
        return key
    def regionalExport(self, key=None):
        if key == None:
            toExprt = {}
            for key,value in self.storage["regionalScope"].items():
                toExprt[self.addPrefToKey(key)] = value
            return toExprt
        else:
            return {
                self.addPrefToKey(key): self.storage["regionalScope"]
            }
    def regionalGetP(self, key=None):
        if key.startswith(self.regionalPrefix):
            return self.regionalGet(key.replace(self.regionalPrefix,"",1))
    # endregion

    # region: sessionStorage.tempmethods
    def tempSet(self, key, value):
        self.storage["tempData"][key] = value
    def tempGet(self, key=None):
        if key == None:
            return self.storage["tempData"]
        else:
            return self.storage["tempData"][key]
    def tempRemove(self, key):
        del self.storage["tempData"][key]
    def tempUpdate(self, newDict):
        self.storage["tempData"].update(newDict)
        return self.storage["tempData"]
    def tempReset(self):
        self.storage["tempData"] = {}
    # endregion
    
    # region: sessionStorage.usermethods
    def userVarSet(self, key, value):
        self.storage["userVars"][key] = value
    def userVarGet(self, key=None):
        if key == None:
            return self.storage["userVars"]
        else:
            return self.storage["userVars"][key]
    def userVarRemove(self, key):
        del self.storage["userVars"][key]
    def userVarUpdate(self, newDict):
        self.storage["userVars"].update(newDict)
        return self.storage["userVars"]
    def userVarReset(self):
        self.storage["userVars"] = {}
    # endregion

class sessionFlags():
    def __init__(self):
        self.flags = []
    def enable(self, flag):
        if flag not in self.flags:
            self.flags.append(flag)
    def disable(self, flag):
        if flag in self.flags:
            self.flags.remove(flag)
    def has(self, flag):
        return flag in self.flags
    def hasnt(self, flag):
        return flag not in self.flags
    def get(self):
        return self.flags
    def __call__(self):
        return self.flags

class crosshellDebugger():
    '''CSlib: Crosshell debugger, this is a text-print based debugging system.'''
    def __init__(self,defaultScope="msg",stripAnsi=False,formatterInstance=None,languageProvider=None):
        self.defScope = defaultScope
        self.scope = defaultScope
        self.stripAnsi = stripAnsi
        # The scopes are are prio listed so if set to 'warn' info and msg will also be shown, to now show set !<mode>
        self.allowedScopes = ["msg","info","warn","exception","error","debug","off"]
        self.colors = {
            "reset":"\033[0m",
            "msg":"",
            "info":"\033[90m",
            "warn":"\033[33m",
            "exception":"\033[91m",
            "error":"\033[91m",
            "debug":"\033[90m",
            "off":"\033[31m"
        }
        self.titles = {
            "msg":"[Crsh]: ",
            "info":"[Crsh]: ",
            "warn":"[Crsh<Warn>]: ",
            "exception":"[Crsh<Exception>]: ",
            "error":"[Crsh<Error>]: ",
            "debug":"[CSDebug]: ",
            "off":"[CSDebug<forcedOutput>]: "
        }
        self.languageProvider = languageProvider
        self.defLanguageProvider = None
        self.formatterInstance = formatterInstance
        self.defFormatterInstance = formatterInstance
    def setScope(self,scope=str):
        if scope not in self.allowedScopes:
            raise Exception(f"Scope {scope} is not allowed, use one of {self.allowedScopes}!")
        else:
            self.scope = scope
    def resetScope(self):
        self.scope = self.defScope
    def setStripAnsi(self,state=bool):
        self.stripAnsi = state
    def setFormatterInstance(self,instance):
        self.formatterInstance = instance
    def resetFormatterInstance(self):
        self.formatterInstance = self.defFormatterInstance
    def setLanguageProvider(self,provider):
        self.languageProvider = provider
    def resetLanguageProvider(self):
        self.languageProvider = self.defLanguageProvider
    def get(self,text,onScope="msg",ct=None,lpReloadMode=None,noPrefix=False):
        if ct != None:
            for key,value in ct.items():
                ct[key] = str(value)
        if ";" in onScope:
            onScope = onScope.split(";")
        else:
            onScope = [onScope]
        scope = self.scope
        if ";" in scope:
            scope = scope.split(";")
        else:
            scope = [scope]
        # list scopes and scopes bellow
        scopes = _returnPrio(self.allowedScopes,scope)
        # any in onScope inside scopes?
        if listItemInList(onScope, scopes) == True:
            #topScope = topPrio(onScope,self.allowedScopes)
            topScope = onScope[0]
            reset = self.colors['reset']
            color = self.colors[topScope]
            if self.stripAnsi == True:
                reset = ""
                color = ""
            title = ""
            if noPrefix == False:
                title = self.titles[topScope]
            if type(text) == str:
                text = text.replace(", txt:",",txt:")
                if text.startswith("lng:"):
                    text = text.replace("lng:","")
                    if self.languageProvider != None:
                        tosend = text.split(",txt:")[0]
                        _text = self.languageProvider.get(tosend,lpReloadMode,ct)
                        if _text != None:
                            text = _text
                        else:
                            if ",txt:" in text:
                                text = text.split(",txt:")[1]
                else:
                    if ",txt:" in text:
                        text = text.split(",txt:")[1]
                    else:
                        text = text.replace("lng:","")
            else:
                text = str(text)
            text = f"{color}{title}{reset}{text}{reset}"
            if self.formatterInstance != None:
                text = self.formatterInstance.parse(text,_stripAnsi=self.stripAnsi,addCustomTags=ct)
            return text
    def print(self,text,onScope="msg",ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        text = self.get(text,onScope,ct,lpReloadMode,noPrefix)
        if text != None:
            if raiseEx == True:
                raise CrosshellDebErr(text)
            else:
                print(text)
    def pmsg(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"msg",ct,lpReloadMode,raiseEx,noPrefix)
    def pinfo(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"info",ct,lpReloadMode,raiseEx,noPrefix)
    def pwarn(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"warn",ct,lpReloadMode,raiseEx,noPrefix)
    def pexception(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"exception",ct,lpReloadMode,raiseEx,noPrefix)
    def perror(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"error",ct,lpReloadMode,raiseEx,noPrefix)
    def pdebug(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"debug",ct,lpReloadMode,raiseEx,noPrefix)
    def poff(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"off",ct,lpReloadMode,raiseEx,noPrefix)

class crshSession():
    # The identification is used on import to ensure classes are compatible.
    global identification; identification = "f09682eb-5be1-4675-b9a0-68148b48e09c"

    def __init__(self, nonRegisterableTypes=["str","list","tuple","dict","int","float","bool","NoneType"], initOnStart=False, regionalVarPrefix="CS_"):
        self.identification = identification

        self.storage = sessionStorage()
        self.tmpSet = self.storage.tempSet
        self.tmpGet = self.storage.tempGet
        self.tmpRemove = self.storage.tempRemove
        self.tmpUpdate = self.storage.tempUpdate
        self.tmpReset = self.storage.tempReset
        self.userVarSet = self.storage.userVarSet
        self.userVarGet = self.storage.userVarGet
        self.userVarRemove = self.storage.userVarRemove
        self.userVarUpdate = self.storage.userVarUpdate
        self.userVarReset = self.storage.userVarReset
        self.regionalSet = self.storage.regionalSet
        self.regionalGet = self.storage.regionalGet
        self.regionalRemove = self.storage.regionalRemove
        self.regionalUpdate = self.storage.regionalUpdate
        self.regionalReset = self.storage.regionalReset
        self.regionalExport = self.storage.regionalExport
        self.regionalGetP = self.storage.regionalGetP

        self.flags = sessionFlags()

        self.registry = {}
        self.nonRegisterableTypes = nonRegisterableTypes

        self.regionalPrefix = self.storage.regionalPrefix = regionalVarPrefix

        self.deb = crosshellDebugger()

        self.initDefaults = {}

        if initOnStart == True:
            self.init()

    def __repr__(self):
        if self.flags.has("--haveBeenInited"):
            crshVer = self.regionalGet("VersionData")
            crshVerId = f'{crshVer["name"]}:{crshVer["vernr"]}_{crshVer["channel"]}:{crshVer["vid"]}'
            return f'<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))} with id {self.identification} for version {crshVerId}>'
        else:
            return f'<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))} with id {self.identification} for version UNSET>'

    def _prepExprt(self):
        """INTERNAL: Preps the data for pickle-export.
        Not used since switched to dill."""
        if self.flags.hasnt("--preppedForExprt"):
            self.regionalSet("Argparser",
                argParse_to_dict(
                    instance = self.regionalGet("Argparser"),
                    parsed = self.regionalGet("Pargs"),
                    orgArgs = self.regionalGet("Args")
                )
            )
            self.flags.enable("--preppedForExprt")
    
    def _postImprt(self,reparse=False):
        """INTERNAL: Post-handle the data from pickle-import.
        Not used since switched to dill."""
        if self.flags.has("--preppedForExprt"):
            parser,parsed = argParse_from_dict(
                import_ = self.regionalGet("Argparser"),
                reparse = reparse
            )
            self.regionalSet("Argparser",parser)
            self.regionalSet("Pargs",parsed)
            self.flags.disable("--preppedForExprt")

    def exprt(self,filename,_mode="dill"):
        """Exports the current session to a file."""
        _mode = "pickle"
        if _mode.lower() == "dill":
            try:
                import dill # local, should have been resolved by init
                _mode = "dill"
            except ImportError: pass
        if _mode.lower() == "json":
            with open(filename, 'w') as f:
                f.write( json.dumps(self.__dict__) )
        else:
            with open(filename, 'wb') as f:
                if _mode.lower() == "dill":
                    dill.dump(self,f)
                else:
                    self._prepExprt()
                    pickle.dump(self,f)

    def imprt(self,filename,_mode="dill"):
        """Imports a session from a file."""
        _mode = "pickle"
        if _mode.lower() == "dill":
            try:
                import dill # local, should have been resolved by init
                _mode = "dill"
            except ImportError: pass
        # fix main-missing
        if sys.modules.get("main") is None:
            sys.modules["main"] = sys.modules[__name__]
        # import
        with open(filename, 'rb') as f:
            if _mode.lower() == "json":
                loaded_session_dict = json.load(f)
            else:
                if _mode.lower() == "dill":
                    loaded_session_dict = dill.load(f).__dict__
                else:
                    loaded_session_dict = pickle.load(f).__dict__
            # Check has-identifier
            if None in [loaded_session_dict.get("identification"), self.__dict__.get("identification")]:
                raise Exception("The session file is not compatible with this version of crosshell. (No identification found)")
            # Check compat
            if loaded_session_dict["identification"] == self.__dict__["identification"]:
                # Update the attributes of the current session with the loaded session
                self.__dict__.update(loaded_session_dict)
                if _mode.lower() == "pickle":
                    self._postImprt()
            else:
                raise Exception("The session file is not compatible with this version of crosshell. (Non-matching session.identtification)")

    def register(self, name, object_):
        """Adds an object to the session-registry."""
        if type(object_) in self.nonRegisterableTypes:
            raise TypeError(f"Objects of type {type(object_)} is not registerable, as it's meant for functions/classInstances and methods. For other types use classStorage.")
        elif isinstance(object_, crshSession):
            raise TypeError("A crosshell-session object cannot be registered, to prevent nesting.")
        self.registry[name] = object_

    def unregister(self, name):
        """Unregisters an object from the session-registry."""
        if self.registry.get(name) != None:
            del self.registry[name]
        else:
            raise KeyError(f"No object with the name '{name}' found in the registry.")
    
    def reset_registry(self):
        """Careful! This will remove all registry items!"""
        self.registry = {}

    def getregister(self,name):
        """Returns the object from the registry."""
        if self.registry.get(name) != None:
            return self.registry[name]
        else:
            raise KeyError(f"No object with the name '{name}' found in the registry.")

    def formatReTagsStr(self,string=str,tags=dict,abs=False):
        for tag,tagValue in tags.items():
            if abs == True:
                string = string.replace(os.path.abspath(tagValue),"{"+tag+"}")
            else:
                string = string.replace(tagValue,"{"+tag+"}")
        return string

    def formatReTagsObj(self,obj=object,tags=dict,abs=False):
        if type(obj) == dict:
            ndict = {}
            for k,v in obj.items():
                ndict[self.formatReTagsObj(k,tags,abs)] = self.formatReTagsObj(v,tags,abs)
            obj = ndict
        elif type(obj) == list:
            nlist = []
            for elem in obj:
                nlist.append(self.formatReTagsObj(elem,tags,abs))
            obj = nlist
        elif type(obj) == tuple:
            ntup = ()
            for elem in obj:
                ntup.append(self.formatReTagsObj(elem,tags,abs))
            obj = ntup
        elif type(obj) == str:
            obj = self.formatReTagsStr(obj,tags,abs)
        return obj

    def getEncoding(self):
        return self.regionalGet("DefaultEncoding")

    def fprint(self,text,file=None,flush=False,end=None,cusPrint=None):
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        toformat, excludes = exclude_nonToFormat(text)
        formatted = self.getregister("txt").parse(toformat)
        text = include_nonToFormat(formatted,excludes)
        if cusPrint == None: cusPrint = print
        if end == None:
            cusPrint(text,file=file,flush=flush)
        else:
            cusPrint(text,end=end,file=file,flush=flush)

    def populateDefaults(self):
        self.flags.enable("--populatedDefaults")

        self.initDefaults["regionalVars"] = {
            "SessionIdentifier": self.identification,
            "DefaultEncoding": "utf-8",
            "RootPathRetrivalMode": "inspect",
            "SettingsReaderMode": "Off",

            "CSlibDir": None,
            "BaseDir": "{CSlibDir}/..",
            "CoreDir": "{BaseDir}/core",
            "AssetsDir": "{BaseDir}/assets",
            "PackagesFolder": "{BaseDir}/packages",
            "mPackPath": "{PackagesFolder}",
            "lPackPath": "{PackagesFolder}/_legacyPackages",
            "ReadersFolder": "{CoreDir}/readers",
            "SettingsFile": "{AssetsDir}/settings.yaml",
            "PersistanceFile": "{AssetsDir}/persistance.yaml",
            "sInputHistoryFile": "{AssetsDir}/.history",
            "CmdletScopeVarsFile": "{CoreDir}/cmdletScopeVars.json",
            "VersionFile": "{CoreDir}/version.yaml",
            "MsgProfileFile": "{AssetsDir}/profile.msg",
            "PyProfileFile": "{AssetsDir}/profile.py",
            "BuiltInReaders": {
                "PLATFORM_EXECUTABLE": "{ReadersFolder}/platexecs.py"
            },

            "Args": None,
            "Startfile": None,
            "Efile": None,
            "Argparser": None,
            "Pargs": None,
            "StripAnsi": None,
            "VerboseStart": None,
            "PythonPath": sys.executable,
            "base_PathTags": None,
            "SubstTags": None,

            "VersionData": None,

            "GetEncoding": self.getEncoding,
            "*fprint": self.fprint,

            "StartupWProgress_steps": 30,
            "StartupWProgress_incr": 3,

            "__registerAsPaths": [ # __registerAsPaths is used to register the paths as pathTags, so any key in this list will be replaceable, for other keys.
                "CSlibDir","BaseDir","CoreDir","AssetsDir","PackagesFolder","mPackPath","lPackPath","ReadersFolder"
            ],
            "__registerAsTags": [ # __registerAsTags is used to register additional substituteTags, not usable when initiating regional-vars.
                "DefaultEncoding", "VersionFile"
            ]
        }

        self.initDefaults["argParser_creationKwargs"] = {
            "prog": "Crosshell",
            "description": "Crosshell Modulo"
        }

        self.initDefaults["arguments"] = [
            [
                ["-sa", "--stripAnsi"],
                {
                    "dest": "stripAnsi",
                    "action": "store_true",
                    "help": "Strips ANSI from output."
                }
            ],
            [
                ["-c", "-cmd"],
                {
                    "dest": "cmd",
                    "help": "Command to execute on start."
                }
            ],
            [
                ["-scr", "-script"],
                {
                    "dest": "script",
                    "help": "Runns a script on start."
                }
            ],
            [
                ["--noverbstart"],
                {
                    "dest": "noverbstart",
                    "action": "store_true",
                    "help": "Suppresses verbose start."
                }
            ],
            [
                ["--noexit"],
                {
                    "dest": "noexit",
                    "action": "store_true",
                    "help": "Keeps crosshell started post cli-command execution."
                }
            ],
            [
                ["--nowelc"],
                {
                    "dest": "nowelc",
                    "action": "store_true",
                    "help": "Suppresses crosshells welcome message."
                }
            ],
            [
                ["--nocls"],
                {
                    "dest": "nocls",
                    "action": "store_true",
                    "help": "Suppresses startup-clear. (if such is enabled in settings)"
                }
            ]
        ]

        self.initDefaults["cmdIdentifier"] = "cmd"

        self.initDefaults["cmdArgPlaceholders"] = {
            "§": " "
        }

        self.initDefaults["aliasIdentifiers"] = {
            "stripAnsi": "StripAnsi",
            "noverbstart": "!VerboseStart"
        }

        self.initDefaults["pathTagBlacklistKeys"] = ["__registerAsPaths","__registerAsTags"]

        self.initDefaults["defaults"] = {
            "settings": {
                "crsh": {
                    "Console.VerboseStart": True,
                    "Console.StripAnsi": False,
                    "Console.DefPrefix": "> ",
                    "Console.DefTitle": "Crosshell Modulo",
                    "Formats.DefaultEncoding": "{CS_DefaultEncoding}",
                    "Version.VerFile": "{CS_VersionFile}",
                    "Version.FileFormatVer": "1",
                    "Parse.Text.Webcolors": True,
                    "CGTS.ANSI_Hex_Palette": "{CS_CGTS_StandardHexPalette}",
                    "CGTS.CustomMappings": {}
                },
                "crsh_debugger": {
                    "Scope": "error"
                }
            },

            "persistance": {
                "crsh": {
                    "Prefix": "@settings:crsh:Console.DefPrefix",
                    "Title": "@settings:crsh:Console.DefTitle"
                }
            }
        }

        self.initDefaults["pipDeps"] = [
            {
                "moduleName": "yaml",
                "pipName": "pyyaml"
            },
            {
                "moduleName": "fuzzywuzzy"
            },
            {
                "moduleName": "dill"
            }
        ]

        self.initDefaults["ingestDefaultTags"] = {
            "CS_CGTS_StandardHexPalette": standardHexPalette,
            "CS_DefaultEncoding": self.initDefaults["regionalVars"]["DefaultEncoding"],
            "CS_VersionFile": normPathSep(prefixAnyTags(self.initDefaults["regionalVars"]["VersionFile"],self.storage.regionalPrefix))
        }

    def ingestDefaults(self,defaults=None,ingestTags=None):
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        if self.flags.has("--populatedDefaults") == False:
            self.populateDefaults()
        if defaults == None:
            defaults = self.initDefaults["defaults"]
        if ingestTags == None:
            ingestTags = self.initDefaults["ingestDefaultTags"]
        ingestDefaults_fd(
            defaults=defaults,
            instanceMapping={
                "settings": {
                    "instance": self.getregister("set"),
                    "tags": ingestTags
                },
                "persistance": {
                    "instance": self.getregister("per"),
                    "tags": ingestTags
                }
            }
        )

    def createAndReturn_startupW(self,pgMax=10,pgIncr=1):
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        return startupMessagingWProgress(
            enabled = self.regionalGet("VerboseStart"),
            stripAnsi = self.flags.has("StripAnsi"),
            debugger = self.deb,
            pgMax = pgMax,
            pgIncr = pgIncr
        )

    def setStripAnsi(self,value=bool):
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        self.regionalSet("StripAnsi",value)
        
    def setVerbStart(self,value=bool):
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        self.regionalSet("VerboseStart",value)

    def init(self, cliArgs=None, regionalVars=None, argumentDeffinionOvw=None, cmdArgPlaceholders=None, pathTagBlacklistKeys=None, additionalSettings=None, additionalPipDeps=None, additionalIngestDefaultTags=None, pipDepsCusPip=None, pipDepsTags=None, launchWith_stripAnsi=False, launchWith_noVerboseStart=False):
        """Initiates the session."""

        if self.flags.has("--populatedDefaults") == False:
            self.populateDefaults()

        # Define standard
        _regionalVars = self.initDefaults["regionalVars"]

        # Deffine Arguments
        _arguments = self.initDefaults["arguments"]

        _cmdArgPlaceholders = self.initDefaults["cmdArgPlaceholders"]

        _pathTagBlacklistKeys = self.initDefaults["pathTagBlacklistKeys"]

        defaults = self.initDefaults["defaults"]

        pipDeps = self.initDefaults["pipDeps"]

        _ingestDefaultTags = self.initDefaults["ingestDefaultTags"]

        if argumentDeffinionOvw != None: _arguments = argumentDeffinionOvw
        if cmdArgPlaceholders != None: _cmdArgPlaceholders.update(cmdArgPlaceholders)
        if pathTagBlacklistKeys != None:
            _pathTagBlacklistKeys.extend(pathTagBlacklistKeys)
        if additionalSettings != None:
            defaults = deep_merge_dict_only(defaults,additionalSettings)
        if additionalPipDeps != None:
            pipDeps.extend(additionalPipDeps)
        if additionalIngestDefaultTags != None:
            _ingestDefaultTags.update(additionalIngestDefaultTags)

        # Get some values
        ## cliargs
        _cliArgs = cliArgs if cliArgs != None else sys.argv
        ## startfile
        _startfile = "Unknown"
        for i,arg in enumerate(_cliArgs):
            if arg.strip().startswith("@startfile:"):
                __startfile = arg.split("@startfile:")[1] 
                if os.path.exists(__startfile):
                    _startfile = __startfile
                    _cliArgs.pop(i)
                else:
                    _cliArgs[i] = __startfile
        ## efile
        if os.path.exists(_cliArgs[0]):
            _efile = _cliArgs[0]
        else:
            _efile = "Unknown"
        _regionalVars["Args"] = _cliArgs
        _regionalVars["Startfile"] = _startfile
        _regionalVars["Efile"] = _efile

        # Get CSlibDir
        _cslibdir = None
        if _regionalVars["RootPathRetrivalMode"] == "inspect":
            if os.path.exists( os.path.abspath(inspect.getfile(inspect.currentframe())) ):
                _cslibdir = os.path.dirname( os.path.abspath(inspect.getfile(inspect.currentframe())) )
            else:
                if os.path.dirname(__file__) == False:
                    _cslibdir = os.path.abspath( os.path.dirname(__file__) )
                else:
                    if os.path.exists(_regionalVars["Args"][0]):
                        _cslibdir = _regionalVars["Args"][0]
        else:
            if os.path.dirname(__file__) == False:
                _cslibdir = os.path.abspath( os.path.dirname(__file__) )
            else:
                if os.path.exists(_regionalVars["Args"][0]):
                    _cslibdir = _regionalVars["Args"][0]

        _regionalVars["CSlibDir"] = _cslibdir

        # Fix substituionTags
        tempSubstTagMan = tagSubstitionManager()
        hasPaths = _regionalVars["__registerAsPaths"]
        def _hasTags(obj):
            hasTags = False
            if type(obj) == dict:
                for key,value in obj.items():
                    if _hasTags(value) == True:
                        hasTags = True
                        break
            elif type(obj) == list or type(obj) == "tuple":
                for i,value in enumerate(obj):
                    if _hasTags(value) == True:
                        hasTags = True
                        break
            elif type(obj) == str:
                if "{" in obj and "}" in obj:
                    hasTags = True
            return hasTags
        def _applySubstTags(instance,obj,keyn="base",blacklistKeys=[]):
            if keyn not in blacklistKeys:
                if type(obj) == dict:
                    for key,value in obj.items():
                        obj[key] = _applySubstTags(instance,value,key,blacklistKeys)
                elif type(obj) == list or type(obj) == "tuple":
                    for i,value in enumerate(obj):
                        obj[i] = _applySubstTags(instance,value,keyn,blacklistKeys)
                elif type(obj) == str:
                    if _hasTags(obj) == True:
                        value = absPathSepObj(tempSubstTagMan.eval(obj))
                    else:
                        value = tempSubstTagMan.eval(obj)
                    value = normPathSep(value)
                    if keyn in hasPaths:
                        tempSubstTagMan.addTag(keyn,value)
                    obj = value
            return obj
        _regionalVars = _applySubstTags(tempSubstTagMan,_regionalVars,blacklistKeys=_pathTagBlacklistKeys)
        initSubstTags = {}
        for key,value in tempSubstTagMan.substTags.items():
            initSubstTags[self.storage.regionalPrefix+key] = value

        _regionalVars["base_PathTags"] = initSubstTags

        # Handle pip dependencies
        _pipDepsCusPip = pipDepsCusPip if pipDepsCusPip != None else sys.executable
        _tagMapping = {
            "CusPip": _pipDepsCusPip
        }
        if pipDepsTags != None: _tagMapping.update(pipDepsTags)
        installPipDeps_fl(
            deps = pipDeps,
            tagMapping = _tagMapping
        )

        # Define argparser
        _argparser = argparse.ArgumentParser(
            **self.initDefaults["argParser_creationKwargs"]
        )
        _regionalVars["Argparser"] = _argparser
        for arg in _arguments:
            _argparser.add_argument(*arg[0], **arg[1])
        _argparser.add_argument('additional', nargs='*', help="Unparsed arguments sent to crosshell.")

        # Parse args
        _regionalVars["Pargs"] = _argparser.parse_args(_cliArgs)

        # Handle placeholders in command and add stripansi
        cmdIndentifier = self.initDefaults["cmdIdentifier"]
        aliasIndentifiers = self.initDefaults["aliasIdentifiers"]
        seenCmd = False
        seenAliases = []
        self.tmpSet("changedValues",[]) # init temporary list of changed values
        for vl in _arguments:
            if vl[1]["dest"] == cmdIndentifier and seenCmd == False:
                for pl,val in _cmdArgPlaceholders.items():
                    attr = getattr(_regionalVars["Pargs"], cmdIndentifier)
                    if attr != None:
                        setattr(_regionalVars["Pargs"], cmdIndentifier, attr.replace(pl,val) )
                for i,arg in enumerate(_regionalVars["Args"]):
                    if arg in vl[0]:
                        if i+1 > len(_regionalVars["Args"])-1: pass
                        else:
                            for pl,val in _cmdArgPlaceholders.items():
                                _regionalVars["Args"][i+1] = _regionalVars["Args"][i+1].replace(val,pl)
                seenCmd = True
                break
        for vl in _arguments:
            dest = vl[1]["dest"]
            if dest in list(aliasIndentifiers.keys()) and dest not in seenAliases:
                key = aliasIndentifiers[dest]
                invertBool = False
                if key.startswith("!"):
                    invertBool = True
                    key = key.replace("!", "", 1)
                if invertBool == True:
                    _v = getattr(_regionalVars["Pargs"], dest)
                    if type(_v) == bool:
                        _regionalVars[key] = not _v
                    else:
                        _regionalVars[key] = _v
                    # add value to temp-list
                    self.tmpSet(
                        "changedValues",
                        [key,*self.tmpGet("changedValues")]
                    )
                else:
                    _regionalVars[key] = getattr(_regionalVars["Pargs"], dest)
                    # add value to temp-list
                    self.tmpSet(
                        "changedValues",
                        [key,*self.tmpGet("changedValues")]
                    )
                seenAliases.append(dest)

        # Append possible custom
        if regionalVars != None: _regionalVars.update(regionalVars)

        # Normalize al paths in values
        _regionalVars = normPathSepObj(_regionalVars)

        # Apply
        self.regionalUpdate(_regionalVars)

        # Handle launchWith
        if launchWith_stripAnsi == True:
            self.regionalSet("StripAnsi", True)
            # Append to changedValues temp-list
            self.tmpSet("changedValues",self.tmpGet("changedValues").append("StripAnsi"))
        if launchWith_noVerboseStart == True:
            self.regionalSet("VerboseStart", False)
            # Append to changedValues temp-list
            self.tmpSet("changedValues",self.tmpGet("changedValues").append("VerboseStart"))

        # Register things
        self.register("base_ptm", pathTagManager(initSubstTags))
        self.getregister("base_ptm").ensureAl()

        _substTags = {}
        for k in self.regionalGet("__registerAsTags"):
            if k in _regionalVars.keys():
                _substTags[self.storage.regionalPrefix+k] = _regionalVars[k]
        self.register("base_stm", tagSubstitionManager(_substTags))

        self.register("stm", collectionalTagManager(initSubstTags,_substTags))
        self.regionalSet("SubstTags", self.getregister("stm").getAlTags() )

        self.register("set", modularSettingsLinker(self.regionalGet("SettingsFile"),encoding=self.regionalGet("DefaultEncoding"),ensure=True,readerMode=self.regionalGet("SettingsReaderMode")))
        self.getregister("set").createFile()
        
        self.register("per", modularSettingsLinker(self.regionalGet("PersistanceFile"),encoding=self.regionalGet("DefaultEncoding"),ensure=True,readerMode=self.regionalGet("SettingsReaderMode")))
        self.getregister("per").createFile()

        # Populate settings and persistance
        ## enable allow flag
        self.flags.enable("--enableUnsafeOperations")
        ## Set
        self.ingestDefaults(defaults,_ingestDefaultTags)
        if "StripAnsi" not in self.tmpGet("changedValues"): # Read temp-list
            self.regionalSet("StripAnsi", self.getregister("set").getProperty("crsh","Console.StripAnsi"))
        if "VerboseStart" not in self.tmpGet("changedValues"): # Read temp-list
            self.regionalSet("VerboseStart", self.getregister("set").getProperty("crsh","Console.VerboseStart"))
        # remove temp-list
            self.tmpRemove("changedValues")
        st = self.createAndReturn_startupW(
            pgMax = self.regionalGet("StartupWProgress_steps"),
            pgIncr= self.regionalGet("StartupWProgress_incr")
        )
        self.deb.setScope(
            self.getregister("set").getProperty("crsh_debugger","Scope")
        )
        ## disable allow flag
        self.flags.disable("--enableUnsafeOperations")

        st.verb("Loading versiondata...") # VERBOSE START

        # Get versionData
        _temp = self.getregister("set").getModule("crsh")
        self.regionalSet(
            "VersionData",
            crosshellVersionManager_getData(
                versionFile = 
                    self.getregister("stm").eval(
                        mode = "ptm",
                        string = getKeyPath(_temp, "Version.VerFile")
                    ),
                formatVersion = getKeyPath(_temp, "Version.FileFormatVer"),
                encoding = getKeyPath(_temp, "Formats.DefaultEncoding")
            )
        )

        st.verb("Loading formatter...") # VERBOSE START

        _temp = self.getregister("set").getModule("crsh")
        _textInst = crosshellGlobalTextSystem(
            pathtagInstance = self.getregister("stm"),
            palette = getKeyPath(_temp,"CGTS.ANSI_Hex_Palette"),
            parseWebcolor = getKeyPath(_temp,"Parse.Text.Webcolors"),
            customTags = getKeyPath(_temp,"CGTS.CustomMappings")
        )

        _textInst.stripAnsi = self.regionalGet("StripAnsi")
        self.deb.setFormatterInstance( _textInst )
        self.register("txt", _textInst)

        st.verb("Does it work? {#DA70D6}*Toad*{r}") # VERBOSE START

        # Set flag
        self.flags.enable("--haveBeenInited")

        # Return
        return self

    def start(self):
        """Starts the set prompt."""
        