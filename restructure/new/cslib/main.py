import pickle, sys, json, os, argparse, inspect, re
from datetime import datetime, timezone

from cslib.piptools import installPipDeps_fl
from cslib._crosshellParsingEngine import tagSubstitionManager, pathTagManager, collectionalTagManager, exclude_nonToFormat, include_nonToFormat
from cslib._crosshellGlobalTextSystem import standardHexPalette,crosshellGlobalTextSystem
from cslib._crosshellMpackageSystem import discoverPackageFiles,installPackageFiles,loadPackageConfig,normFeatureDataAndReg,loadPackageFeatures
from cslib.externalLibs.filesys import filesys
from cslib.externalLibs.conUtils import getConSize
from cslib.datafiles import _fileHandler,setKeyPath,getKeyPath
from cslib.exportImport_tools import argParse_to_dict,argParse_from_dict
from cslib.pathtools import normPathSep,normPathSepObj,absPathSepObj
from cslib.progressMsg import startupMessagingWProgress
from cslib.exceptions import CrosshellDebErr
from cslib.types import expectedList
from cslib.customImplements import readerMangler,cmdletMangler,langpckMangler
from cslib.platformAndOS import handleOSinExtensionsList

class stateInstance():
    """Supporting class for hosting data inplace of files."""
    def __init__(self,mode="dict",dict_data={},stream_data=None,stream_appending=False,stream_asbytes=False,stream_filename="stateInstance.any",encoding="utf-8",parent=None,parentKeepList=None):
        self.modes = ["dict","stream"]
        if mode not in self.modes: raise Exception(f"Mode '{mode}' is not supported, use one of {self.modes}")
        self.parent = parent
        self.data = None
        self.mode = mode
        if self.mode == "dict":
            self.data = dict_data
        elif self.mode == "stream":
            if stream_data != None:
                self.data = stream_data
            else:
                self.data = b'' if stream_asbytes else ''
        self.stream_appending = stream_appending
        self.stream_asbytes = stream_asbytes
        self.encoding = encoding
        self.filename = stream_filename
        if parentKeepList != None:
            parentKeepList.append(self)
    def _onNoneRaise(self):
        if self.data == None:
            raise Exception("Data is None, can't perform operation. (Probably inited with the wrong mode)")
    def __repr__(self):
        strBuild = f"<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))} of type {self.mode}"
        if self.mode == "stream":
            if self.stream_appending == True and self.stream_asbytes == True:
                strBuild += ".appendingBytes"
            elif self.stream_appending == True and self.stream_asbytes == False:
                strBuild += ".appendingString"
            elif self.stream_appending == False and self.stream_asbytes == True:
                strBuild += ".bytes"
            elif self.stream_appending == False and self.stream_asbytes == False:
                strBuild += ".string"
            if self.filename not in ["" , None, "stateInstance.any"]:
                strBuild += f" for '{self.filename}'"
        strBuild += ">"
        return strBuild

    def __setitem__(self, key, value):
        self._onNoneRaise()
        if self.mode == "dict":
            self.data[key] = value
        else:
            raise Exception(f"Operation is not supported for mode '{self.mode}' only for 'dict'!")
    def __getitem__(self, key=None):
        self._onNoneRaise()
        if self.mode == "dict":
            if key == None:
                return self.data
            else:
                if key in self.data.keys():
                    return self.data[key]
                else:
                    return None
        else:
            raise Exception(f"Operation is not supported for mode '{self.mode}' only for 'dict'!")
    def remove(self, key=None):
        self._onNoneRaise()
        if self.mode == "dict":
            if key in self.data.keys():
                del self.data[key]
        else:
            raise Exception(f"Operation is not supported for mode '{self.mode}' only for 'dict'!")
    def update(self,newDict):
        self._onNoneRaise()
        if self.mode == "dict":
            self.data.update(newDict)
        else:
            raise Exception(f"Operation is not supported for mode '{self.mode}' only for 'dict'!")

    def write(self,binaryOrString):
        self._onNoneRaise()
        #stream
        if self.mode == "stream":
            #stream.appending
            if self.stream_appending == True:
                #stream.appening.bytes
                if type(binaryOrString) == bytes:
                    #stream.appending.bytes.asbinary
                    if self.stream_asbytes == True:
                        self.data += binaryOrString
                    #stream.appending.bytes.asstring
                    else:
                        self.data += binaryOrString.decode(self.encoding)
                #stream.appening.string
                else:
                    #stream.appending.string.asbinary
                    if self.stream_asbytes == True:
                        self.data += binaryOrString.encode(self.encoding)
                    #stream.appending.string.asstring
                    else:
                        self.data += binaryOrString
            #stream.overwrite
            else:
                #stream.overwrite.bytes
                if type(binaryOrString) == bytes:
                    #stream.overwrite.bytes.asbinary
                    if self.stream_asbytes == True:
                        self.data = binaryOrString
                    #stream.overwrite.bytes.asstring
                    else:
                        self.data = binaryOrString.decode(self.encoding)
                #stream.overwrite.string
                else:
                    #stream.overwrite.string.asbinary
                    if self.stream_asbytes == True:
                        self.data = binaryOrString.encode(self.encoding)
                    #stream.overwrite.string.asstring
                    else:
                        self.data = binaryOrString
        else:
            raise Exception(f"Operation is not supported for mode '{self.mode}' only for 'stream'!")
    def read(self):
        self._onNoneRaise()
        if self.mode == "stream":
            #binary
            if type(self.data) == bytes:
                #binary.asbinary
                if self.stream_asbytes == True:
                    return self.data
                #binary.asstring
                else:
                    return self.data.decode(self.encoding)
            #string
            else:
                #string.asbinary
                if self.stream_asbytes == True:
                    return self.data.encode(self.encoding)
                #string.asstring
                else:
                    return self.data
        else:
            raise Exception(f"Operation is not supported for mode '{self.mode}' only for 'stream'!")
    def close(self):
        self._onNoneRaise()
        if self.mode == "stream":
            pass
        else:
            raise Exception(f"Operation is not supported for mode '{self.mode}' only for 'stream'!")
    
    def get(self,key=None):
        if key != None:
            if self.mode == "dict":
                return self.__getitem__(key)
            else:
                return self.data[key]
        else:
            return self.data
    def getStr(self):
        if self.mode == "dict":
            return json.dumps(self.data)
        else:
            _toRet = self.read()
            if type(_toRet) == bytes:
                _toRet = _toRet.decode(self.encoding)
            else:
                _toRet = str(_toRet)
            return _toRet
    def getJson(self):
        if self.mode == "dict":
            return json.dumps(self.data)
        else:
            _str = self.getStr()
            if _str.startswith("{") and _str.endswith("}"): pass
            else:
                _str = "{"+_str+"}"
            return _str
    def getForcedDict(self):
        if self.mode == "dict":
            return self.data
        else:
            return json.loads(self.getJson())

class pathObject():
    def __init__(self,defaults=None):
        if defaults != None:
            data = defaults
        else:
            data = []
        self.data = data
    def set(self,data=list):
        self.data = data
    def get(self):
        return self.data
    def extend(self,data):
        self.data.extend(data)
    def append(self,data):
        self.data.append(data)
    def ensureAl(self):
        for path in self.data:
            filesys.ensureDirPath(path)

class modularSettingsLinker():
    '''CSlib: Links to a settings file to provide a module system'''
    def __init__(self,settingsFile,encoding="utf-8",ensure=False,readerMode="Comments",discardNewlines=False,stm=None,fileIsStream=False,streamType="yaml"):
        self.file = settingsFile
        self.modules = []
        self.encoding = encoding
        self.fileIsStream = fileIsStream
        if self.fileIsStream == True:
            self.filetype = streamType
        else:
            if ".yaml" in self.file:
                self.filetype = "yaml"
            elif ".json" in self.file or ".jsonc" in self.file or ".json5" in self.file:
                self.filetype = "json"
        if self.fileIsStream == False and ensure == True:
            if os.path.exists(self.file) != True:
                toc = ""
                if self.filetype == "json":
                    toc = "{}"
                open(self.file,'w',encoding=encoding).write(toc)
        self.readerMode = readerMode
        self.discardNewlines = discardNewlines
        self.keptComments = None
        self.tagMan = stm
        if self.fileIsStream == False and os.path.exists(self.file) == False: open(self.file,'x').write("")
    def _getContent(self,_ovFile=None,_ovEnc=None) -> dict:
        toUse = _ovFile if _ovFile != None else self.file
        encoding = _ovEnc if _ovEnc != None else self.encoding
        data = {}
        if self.readerMode.lower() != "off":
            data,self.keptComments = _fileHandler(self.filetype,"get",toUse,encoding=encoding,readerMode=self.readerMode,discardNewlines=self.discardNewlines,fileIsStream=self.fileIsStream)
        else:
            data = _fileHandler(self.filetype,"get",toUse,encoding=encoding,readerMode=self.readerMode,fileIsStream=self.fileIsStream)
        if data == None: data = {}
        return data
    def _setContent(self,content,_ovFile=None,_ovEnc=None) -> None:
        toUse = _ovFile if _ovFile != None else self.file
        encoding = _ovEnc if _ovEnc != None else self.encoding
        if self.readerMode.lower() != "off":
            _fileHandler(self.filetype,"set",toUse,content,encoding=encoding,readerMode=self.readerMode,discardNewlines=self.discardNewlines,commentsToInclude=self.keptComments,fileIsStream=self.fileIsStream)
        else:
            _fileHandler(self.filetype,"set",toUse,content,encoding=encoding,readerMode=self.readerMode,fileIsStream=self.fileIsStream)
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
    def _runThroughTagMan(self,data,extraTags=None):
        if self.tagMan != None:
            if type(data) == str:
                if self.tagMan.idef == "collection":
                    data = self.tagMan.evalDataAl(data,extraTags)
                else:
                    data = self.tagMan.evalData(data,extraTags)
            elif type(data) in [tuple,list]:
                for i in range(len(data)):
                    if self.tagMan.idef == "collection":
                        data[i] = self.tagMan.evalDataAl(data[i],extraTags)
                    else:
                        data[i] = self.tagMan.evalData(data[i],extraTags)
            elif type(data) == dict:
                for i in data.keys():
                    if self.tagMan.idef == "collection":
                        data[i] = self.tagMan.evalDataAl(data[i],extraTags)
                    else:
                        data[i] = self.tagMan.evalData(data[i],extraTags)
        return data
    def createFile(self,overwrite=False):
        if self.fileIsStream != True:
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
    def getModule(self,module,skipTagMan=False,extraTags=None) -> None:
        data = self._getContent()
        toRet = data[module]
        if skipTagMan == False: toRet = self._runThroughTagMan(toRet,extraTags=None)
        return toRet
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
    def get(self,module,autocreate=False,skipTagMan=False,extraTags=None) -> dict:
        if module in self.modules:
            data = self._getContent()
            toRet = data[module]
            if skipTagMan == False: toRet = self._runThroughTagMan(toRet,extraTags=None)
            return toRet
        elif autocreate == True:
            self.addModule(module)
            data = self._getContent()
            toRet = data[module]
            if skipTagMan == False: toRet = self._runThroughTagMan(toRet,extraTags=None)
            return toRet
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
        data = self.get(module,autocreate=autocreate,skipTagMan=True)
        data = setKeyPath(data,keyPath,default)
        self.set(module,data,autocreate=autocreate)
    def getProperty(self,module,keyPath,autocreate=False,skipTagMan=False,extraTags=None):
        data = self.get(module,autocreate=autocreate,skipTagMan=True)
        toRet = getKeyPath(data,keyPath)
        if skipTagMan == False: toRet = self._runThroughTagMan(toRet,extraTags=None)
        return toRet
    def chnProperty(self,module,keyPath,default,autocreate=False) -> None:
        data = self.get(module,autocreate=autocreate,skipTagMan=True)
        data = setKeyPath(data,keyPath,default,nonAppend=True)
        self.set(module,data,autocreate=autocreate)
    def uppProperty(self,module,keyPath,default,autocreate=False) -> None:
        data = self.get(module,autocreate=autocreate,skipTagMan=True)
        data = setKeyPath(data,keyPath,default,update=True)
        self.set(module,data,autocreate=autocreate)
    def remProperty(self,module,keyPath,autocreate=False) -> None:
        data = self.get(module,autocreate=autocreate,skipTagMan=True)
        data = remKeyPath(data,keyPath)
        self.set(module,data,autocreate=autocreate)

def populateLanguageList(languageListFile,langPath,listFormat="json",langFormat="json",keepExisting=False,encoding="utf-8",fileIsStream=False):
    '''CSlib: Function to populate a language list.'''
    orgLangList = _fileHandler(listFormat,"get",languageListFile,encoding=encoding,fileIsStream=fileIsStream)
    LangList = orgLangList.copy()
    try:
        for path in langPath.get():
            if filesys.doesExist(path):
                objects = filesys.scantree(path)
                for object in objects:
                    fending = filesys.getFileExtension(object.name)
                    name = filesys.getFileName(object.name)
                    if fending == langFormat:
                        if keepExisting == True:
                            if LangList.get(name) == None:
                                LangList[name] = object.path
                        else:
                            LangList[name] = object.path
    except:
        LangList = orgLangList
    _fileHandler(listFormat,"set",languageListFile,LangList,encoding=encoding,fileIsStream=fileIsStream)

def recheckLanguageList(languageListFile,listFormat=None,returnDontRemove=False,encoding="utf-8",fileIsStream=False):
    '''CSlib: Checks over a languagelist so al the entries exist, and removses those who don't'''
    if returnDontRemove == True:
        missing = []
    else:
        languageList = _fileHandler(listFormat, "get", languageListFile,encoding=encoding,fileIsStream=fileIsStream)
        newLanguageList = languageList.copy()
    for entry,path in languageList.items():
        if type(path) != dict:
            if filesys.notExist(path):
                if returnDontRemove == True:
                    missing.append({entry:path})
                else:
                    newLanguageList.pop(entry)
    if returnDontRemove == True:
        return missing
    else:
        _fileHandler(listFormat, "set", languageListFile, newLanguageList,encoding=encoding,fileIsStream=fileIsStream)

def _handleAnsi(text):
    '''CSlib: Smal function to handle the &<ansi>m format.'''
    return re.sub(r'&(\d+)m', r'\033[\1m', text)

class crosshellLanguageProvider():
    '''CSlib: Crosshell language system.'''
    def __init__(self,languageListFile,defaultLanguage="en-us",listFormat="json",langFormat="json",pathtagManInstance=None,langPath=None,encoding="utf-8",sameSuffixLoading=False,fileIsStream=False):
        # Save
        self.languageListFile = languageListFile
        self.fileIsStream = fileIsStream
        if self.fileIsStream != True:
            if os.path.exists(self.languageListFile) == False:
                filesys.createFile(self.languageListFile)
                if listFormat == "json":
                    open(self.languageListFile,'w').write("{}")
        self.defLanguage = self.parseSingleLanguage(defaultLanguage)
        self.listFormat = listFormat
        self.langFormat = langFormat
        self.pathtagManInstance = pathtagManInstance
        self.langPath = langPath
        self.encoding = encoding
        self.sameSuffixLoading = sameSuffixLoading
        # Retrive languageList after rechecking it
        recheckLanguageList(self.languageListFile,self.listFormat,encoding=self.encoding,fileIsStream=self.fileIsStream)
        self.languageList = _fileHandler(self.listFormat,"get",self.languageListFile,encoding=self.encoding,fileIsStream=self.fileIsStream)
        # Set default language
        self.languagePrios = defaultLanguage
        self.language = self.defLanguage
        # setup choices
        self.choices = []
        self.populateChoices()
        # populate priority listing with any same-suffix names (if enabled)
        if sameSuffixLoading == True:
            self.loadSameSuffixedLanguages()
        # Load language
        self.load()
    def parseSingleLanguage(self,unparsed):
        if type(unparsed) == str:
            return {"1":unparsed}
        else:
            return unparsed
    def populateChoices(self):
        for key in self.languageList.keys():
            if key not in self.languagePrios.values():
                self.choices.append(key)
    def loadSameSuffixedLanguages(self):
        for name in self.languageList.keys():
            _suffix = name.split("_")
            suffix = _suffix[-1].strip(" ")
            current = self.languagePrios.values()
            if suffix != name and suffix in current and name not in current:
                heigestkey = None
                for key in self.languagePrios.keys():
                    try:
                        int(key)
                        if heigestkey == None:
                            heigestkey = int(key)
                        elif int(key) > heigestkey:
                            heigestkey = int(key)
                    except: pass
                self.languagePrios[str(heigestkey+1)] = name
            del current
    def loadLanguagePriorityList(self):
        mergedLanguage = {}
        languages = [value for key, value in sorted(list(self.languagePrios.items()), key=lambda x: int(x[0]))]
        languages = languages[::-1] # Reverse
        for lang in languages:
            langData = self._load(self.languageList,lang,self.pathtagManInstance,self.langFormat)
            mergedLanguage.update(langData)
        return mergedLanguage
    def populateList(self,keepExisting=False,reload=True):
        if self.langPath != None:
            populateLanguageList(self.languageListFile,self.langPath,self.listFormat,self.langFormat,keepExisting=keepExisting,encoding=self.encoding,fileIsStream=self.fileIsStream)
            if reload == True:
                self.relist()
                self.load()
    def relist(self):
        '''Reloads the languageList.'''
        self.languageList = _fileHandler("json","get",self.languageListFile,encoding=self.encoding,fileIsStream=self.fileIsStream)
    def _ptmEval(self,instance,inp,extras=None):
        if isinstance(inp,stateInstance):
            _inp = inp.getStr()
        else:
            if type(inp) == dict:
                _inp = json.dumps(inp)
            else:
                _inp = inp
        if instance.idef == "collection":
            _inp = instance.evalAl(_inp,extras)
        else:
            _inp = instance.eval(_inp,extras)
        if isinstance(inp,stateInstance):
            inp.data = _inp
            _inp = inp
        else:
            if type(inp) == dict:
                _inp = json.loads(_inp)
        return _inp
    def _load(self,languagelist,language,pathtagManInstance,langFormat):
        if languagelist.get(language) != None:
            if isinstance(languagelist[language],stateInstance):
                _isStream = True
            else:
                _isStream = False
            if type(languagelist[language]) == dict:
                if pathtagManInstance == None:
                    languageData = languagelist[language]
                else:
                    languageData = self._ptmEval(pathtagManInstance,languagelist[language])
            else:
                if pathtagManInstance == None:
                    languageData = _fileHandler(langFormat,"get",languagelist[language],encoding=self.encoding,fileIsStream=_isStream)
                else:
                    languageData = _fileHandler(langFormat,"get",self._ptmEval(self.pathtagManInstance,languagelist[language]),encoding=self.encoding,fileIsStream=_isStream)
        else:
            languageData = {}
        return languageData
    def load(self):
        '''Retrives the languageFile from the languageList and proceeds to load the language.'''
        self.languageData = self.loadLanguagePriorityList()
    def setLang(self,language):
        '''Set the language.'''
        self.language = self.parseSingleLanguage(language)
        self.languagePrios = self.language # fix?
        self.load()
    def resLang(self):
        '''Reset the language.'''
        self.language = self.defLanguage.copy()
        self.languagePrios = self.language # fix?
        self.load()
    def _handleAnsi(self,text):
        return _handleAnsi(text)
    def _handlePathTags(self,text,extraPathTags=None):
        return self._ptmEval(self.pathtagManInstance,text,extraPathTags)
    def _handle(self,text,extraPathTags=None):
        if text != None:
            text = self._handleAnsi(text)
            text = self._handlePathTags(text,extraPathTags)
        return text
    def _handle_rollings(self,req):
        matches = []
        for key in self.languageData.keys():
            if key.startswith(req):
                matches.append(key)
        if matches == []:
            return req
        else:
            return self.languageData.get(random.choice(matches))
    def print(self,textId,defaultText=None,reloadMode="None",ept=None):
        '''Prints a text from the current language, and if needed reloads the language. reloadMode can be 'lang', 'list' or 'both' '''
        if reloadMode == "lang":
            self.load()
        elif reloadMode == "list":
            self.relist()
        elif reloadMode == "both":
            self.relist()
            self.load()
        try:
            if textId.endswith("_rolling_"):
                text = self._handle_rollings(textId)
            else:
                text = self.languageData.get(textId)
            text = self._handle(text,ept)
            if text == None and type(text) == str:
                print(self._handle(defaultText,ept))
            else:
                print(text)
        except:
            print(self._handle(defaultText,ept))
    def get(self,textId,reloadMode="None",ept=None):
        '''Gets a text from the current language, and if needed reloads the language. reloadMode can be 'lang', 'list' or 'both' '''
        if reloadMode == "lang":
            self.load()
        elif reloadMode == "list":
            self.relist()
        elif reloadMode == "both":
            self.relist()
            self.load()
        if textId.endswith("_rolling_"):
            text = self._handle_rollings(textId)
        else:
            text = self.languageData.get(textId)
        text = self._handle(text,ept)
        return text
    def getLanguageData(self) -> dict:
        _ld = {}
        _ld["name"] = self.get("lang_name")
        _ld["author"] = self.get("lang_author")
        _ld["code"] = self.get("lang_code")
        _ld["format"] = self.get("lang_format")
        return _ld

    def injectLanguage(self,name,languageData,useStateInstances=False):
        if useStateInstances == True:
            listContent = _fileHandler(self.listFormat,"get",self.languageListFile,encoding=self.encoding,fileIsStream=self.fileIsStream) # get list
            _obj = stateInstance(mode="stream",stream_filename=name+"."+self.langFormat,parent=self,encoding=self.encoding)               # create obj
            _fileHandler(self.langFormat,"set",_obj,languageData,encoding=self.encoding,fileIsStream=True)                                # write data to obj
            listContent[name] = _obj.getForcedDict()                                                                                      # add obj to list
            _fileHandler(self.listFormat,"set",self.languageListFile,listContent,encoding=self.encoding,fileIsStream=self.fileIsStream)   # save list
        else:
            listContent = _fileHandler(self.listFormat,"get",self.languageListFile,encoding=self.encoding,fileIsStream=self.fileIsStream) # get list
            listContent[name] = languageData                                                                                              # add data to list
            _fileHandler(self.listFormat,"set",self.languageListFile,listContent,encoding=self.encoding,fileIsStream=self.fileIsStream)   # save list
        
        self.relist()
        self.populateChoices()

def recursiveMultipleReplacementTagWrapper(obj,tags=dict):
    """CSlib: Evals an object in multiple replacementTagWrappers."""
    if type(obj) == dict:
        for k,v in obj.items():
            obj[k] = recursiveMultipleReplacementTagWrapper(v,tags)
    elif type(obj) == list or type(obj) == tuple:
        for i,v in enumerate(obj):
            obj[i] = recursiveMultipleReplacementTagWrapper(v,tags)
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

def handleOSinExtensionsList(extensions=list) -> list:
    """CSlib: Smal function for checking os-specific extensions.
    Handling extension prefixes like 'win@' and if os dosen't match will exlcude it."""
    newList = []
    for extension in extensions:
        # multi
        if "win;mac@" in extension:
            if IsWindows() == True or IsMacOS() == True:
                newList.append( extension.replace("win;mac@","") )
        elif "win;lnx@" in extension:
            if IsWindows() == True or IsLinux() == True:
                newList.append( extension.replace("win;lnx@","") )
        elif "mac;lnx@" in extension:
            if IsMacOS() == True or IsLinux() == True:
                newList.append( extension.replace("mac;lnx@","") )
        elif "lnx;mac@" in extension:
            if IsMacOS() == True or IsLinux() == True:
                newList.append( extension.replace("lnx;mac@","") )
        # single
        elif "win@" in extension:
            if IsWindows() == True:
                newList.append( extension.replace("win@","") )
        elif "mac@" in extension:
            if IsMacOS() == True:
                newList.append( extension.replace("mac@","") )
        elif "lnx@" in extension:
            if IsLinux() == True:
                newList.append( extension.replace("lnx@","") )
        # all
        elif "all@" in extension:
            newList.append( extension.replace("all@","") )
        # fallback
        else:
            newList.append(extension)
    return newList

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

def getReaderExecutable(name,readerFile,encoding="utf-8", isStream=False) -> str:
    '''CSlib: Smal function to get the reader-executable from using its name'''
    # ensuring valid data
    if isStream == False:
        if os.path.exists(readerFile) == False:
            open(readerFile,'x').write("{}")
    else:
        if readerFile.read() in [None,""]: readerFile.write("{}")
    # read
    readers = _fileHandler("json", "get", readerFile, encoding=encoding, safeSeps=True, fileIsStream=isStream)
    if readers.get(name) != None:
        return readers.get(name)
    else:
        return None

def toReaderFormat(dictFromSettings,readerFile,encoding="utf-8",isStream=False) -> list:
    '''CSlib: Smal function for to convert the reader part of settings to the correct format.'''
    readerData = []
    for reader,extensions in dictFromSettings.items():
        readerData.append( {"name":reader,"exec":getReaderExecutable(reader, readerFile, encoding, isStream),"extensions":expectedList(extensions)} )
    return readerData

def addReader(name,execPath,readerFile,encoding="utf-8",isStream=False):
    '''CSlib: Smal function to add a reader to the readerFile'''
    readers = _fileHandler("json", "get", readerFile, encoding=encoding, safeSeps=True, fileIsStream=isStream)
    readers[name] = execPath
    _fileHandler("json", "set", readerFile, readers, encoding=encoding, fileIsStream=isStream)

class sessionStorage():
    def __init__(self,regionalPrefix=""):
        self.regionalPrefix = regionalPrefix
        self.storage = {
            "tempData": {},
            "userVars": {},
            "regionalScope": {},
            "pkgReg": {}
        }
    # region: sessionStorage.mainmethods
    def reset(self, key=None):
        if key == None:
            self.storage = {
                "tempData": {},
                "userVars": {},
                "regionalScope": {},
                "pkgReg": {}
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
            toExprt = {}
            for k,v in self.storage["regionalScope"].items():
                if k.strip().startswith("*"):
                    k = k.replace("*","",1)
                toExprt[k] = v
            return toExprt
        else:
            if key not in self.storage["regionalScope"].keys():
                key = key.replace("*","",1)
            try:
                _v = self.storage["regionalScope"][key]
            except KeyError:
                _v = self.storage["regionalScope"]["*"+key]
            return _v
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
            key = self.regionalPrefix + key
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

    # region: sessionStorage.pkgRegmethods
    def featureIsRegistered(self,name):
        return self.storage["pkgReg"].get(name) != None
    def regFeature(self,name,config={}):
        if not self.featureIsRegistered(name):
            self.storage["pkgReg"][name] = {}
            self.storage["pkgReg"][name]["config"] = config
            self.storage["pkgReg"][name]["data"] = {}
        else:
            raise Exception(f"Feature '{name}' is already registered, use uppFeature or unregFeature to manage it.")
    def unregFeature(self,name):
        if self.featureIsRegistered(name):
            del self.storage["pkgReg"][name]
        else:
            raise Exception(f"Feature '{name}' isn't registered, use regFeature to register it.")
    def uppFeatureConfig(self,name,config=dict):
        if self.featureIsRegistered(name):
            self.storage["pkgReg"][name]["config"] = config
        else:
            raise Exception(f"Feature '{name}' isn't registered, use regFeature to register it.")
    def uppFeatureData(self,name,data=dict):
        if self.featureIsRegistered(name):
            self.storage["pkgReg"][name]["data"] = data
        else:
            raise Exception(f"Feature '{name}' isn't registered, use regFeature to register it.")
    def configFeature(self,name,key,value):
        if self.featureIsRegistered(name):
            self.storage["pkgReg"][name]["config"][key] = value
        else:
            raise Exception(f"Feature '{name}' isn't registered, use regFeature to register it.")
    def getFeatures(self) -> dict:
        return self.storage["pkgReg"]
    def uppFeatures(self,pkgReg=dict):
        self.storage["pkgReg"].update(pkgReg)
    def getFeatureConfig(self,name) -> dict:
        if self.featureIsRegistered(name):
            return self.storage["pkgReg"][name]["config"]
        else:
            raise Exception(f"Feature '{name}' isn't registered, use regFeature to register it.")
    def getFeatureData(self,name) -> dict:
        if self.featureIsRegistered(name):
            return self.storage["pkgReg"][name]["data"]
        else:
            raise Exception(f"Feature '{name}' isn't registered, use regFeature to register it.")
    def getFeatureDataForPackage(self,name,pkgid) -> list:
        if self.featureIsRegistered(name):
            if self.storage["pkgReg"][name]["data"].get(pkgid) != None:
                return self.storage["pkgReg"][name]["data"][pkgid]
        else:
            raise Exception(f"Feature '{name}' isn't registered, use regFeature to register it.")
    def getPackagesForFeature(self,name) -> list:
        if self.featureIsRegistered(name):
            return list(self.storage["pkgReg"][name]["data"].keys())
        else:
            raise Exception(f"Feature '{name}' isn't registered, use regFeature to register it.")
    def registerPackageForFeature(self,name,pkgid,data={}):
        if self.featureIsRegistered(name):
            self.storage["pkgReg"][name]["data"][pkgid] = data
        else:
            raise Exception(f"Feature '{name}' isn't registered, use regFeature to register it.")
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

class log2File():
    def __init__(self,filepath,logType="text",encoding="utf-8",fileIsStream=False,timeForceUTC=False):
        allowedLogTypes = ["text","json"]
        self.logType = logType
        if self.logType not in allowedLogTypes:
            raise Exception(f"Log type '{logType}' is not allowed, use one of {allowedLogTypes}")
        self.filepath = filepath
        self.encoding = encoding
        self.fileIsStream = fileIsStream
        self.forceUTC = timeForceUTC
        self._setMeta()
    def _getTime(self):
        if self.forceUTC == True:
            return datetime.now(timezone.utc)
        else:
            return datetime.now(timezone.utc).replace(tzinfo=None)
    def _getTimeStamp(self,format_="log"):
        current_datetime = self._getTime()
        if format_ == "meta":
            return current_datetime.strftime('%d-%m-%Y %H:%M:%S') # 01-01-2021 00:00:00
        elif format_ == "log":
            return current_datetime.strftime('%d-%m-%Y_%H:%M:%S') # 01-01-2021_00:00:00
        else:
            return str(current_datetime)
    def _hasMeta(self):
        if self.logType == "json":
            if filesys.doesExist(self.filepath): data = _fileHandler("json","get",self.filepath,encoding=self.encoding,fileIsStream=self.fileIsStream)
            else: data = {}
            if data.get("meta") != None:
                return True
            else:
                return False
        else:
            if self.fileIsStream == True:
                _tx = self.filepath.data
            else:
                if filesys.doesExist(self.filepath): _tx = filesys.readFromFile(self.filepath)
                else: _tx = ""
            fline = None
            for line in _tx.split("\n"):
                if line.strip().startswith("# log2File.LogFile, "):
                    fline = line
                    break
            if fline != None:
                return True
            else:
                return False
    def _setMeta(self):
        if self._hasMeta() == False:
            if self.logType == "json":
                meta = {
                    "name": "log2File: Logfile",
                    "format": 1,
                    "knownAsStream": self.fileIsStream,
                    "created": self._getTimeStamp("meta")
                }
                if filesys.doesExist(self.filepath): current = _fileHandler("json","get",self.filepath,encoding=self.encoding,fileIsStream=self.fileIsStream)
                else: current = {}
                new = dict()
                new["meta"] = meta
                new.update(current)
                _fileHandler("json","set",self.filepath,new,encoding=self.encoding,fileIsStream=self.fileIsStream)
            else:
                meta = f"# log2File.LogFile, format:1, knownAsStream:{self.fileIsStream}, created:{self._getTimeStamp('meta')}"
                if self.fileIsStream == True:
                    current = self.filepath.data
                    new = meta + "\n" + current
                    self.filepath.data = new
                else:
                    if filesys.doesExist(self.filepath): current = filesys.readFromFile(self.filepath)
                    else: current = ""
                    new = meta + "\n" + current
                    if filesys.notExist(self.filepath): filesys.createFile(self.filepath)
                    filesys.writeToFile(new,self.filepath)
    def _getObjAsDict(self,obj):
        return obj.__dict__
    def _getObjAsDictRecurs(self,obj):
        new = obj.__dict__
        for k,v in new.items():
            if type(v) not in [str,int,float,bool]:
                new[k] = self._getObjAsDictRecurs(v)
        return new
    def write(self,logData,prefix="%t"):
        prefix = prefix.replace("%t",self._getTimeStamp('log'))
        if self.logType == "text":
            if type(logData) not in [str,int,float,bool,list,tuple,dict]:
                logData = self._getObjAsDictRecurs(logData)
            if type(logData) != str:
                logData = json.dumps(logData)
            if self.fileIsStream == True:
                current = self.filepath.data
                new = current + "\n" + f"[{prefix}] {logData}"
                self.filepath.data = new
            else:
                if filesys.doesExist(self.filepath): current = filesys.readFromFile(self.filepath)
                new = current + "\n" + f"[{prefix}] {logData}"
                if filesys.notExist(self.filepath): filesys.createFile(self.filepath)
                filesys.writeToFile(new,self.filepath)
        else:
            if type(logData) not in [str,int,float,bool,list,tuple,dict]:
                logData = self._getObjAsDict(logData)
            current = _fileHandler("json","get",self.filepath,encoding=self.encoding,fileIsStream=self.fileIsStream)
            current[prefix] = logData
            _fileHandler("json","set",self.filepath,current,encoding=self.encoding,fileIsStream=self.fileIsStream)
    def read(self):
        if self.logType == "text":
            if self.fileIsStream == True:
                _tx = self.filepath.data
            else:
                _tx = filesys.readFromFile(self.filepath)
            nlines = []
            for line in _tx.split("\n"):
                if not line.strip().startswith("#"):
                    nlines.append(line)
            return "\n".join(nlines)
        else:
            _dict = _fileHandler("json","get",self.filepath,encoding=self.encoding,fileIsStream=self.fileIsStream)
            if _dict.get("meta") != None:
                _dict.pop("meta")
            return _dict
    def getMeta(self):
        if self.logType == "text":
            if self.fileIsStream == True:
                _tx = self.filepath.data
            else:
                _tx = filesys.readFromFile(self.filepath)
            fline = None
            for line in _tx.split("\n"):
                if line.strip().startswith("# log2File.LogFile, "):
                    fline = line.replace("# log2File.LogFile, ","")
                    break
            if fline != None:
                parts = fline.split(",")
                meta = {}
                for part in parts:
                    part = part.strip()
                    if ":" in part:
                        key = part.split(":")[0]
                        value = part.split(":")[1]
                        meta[key] = value
                return meta
            else:
                return fline
        else:
            _dict = _fileHandler("json","get",self.filepath,encoding=self.encoding,fileIsStream=self.fileIsStream)
            return _dict.get("meta")
                    
class crosshellDebugger():
    '''CSlib: Crosshell debugger, this is a text-print based debugging system.'''
    def __init__(self,defaultScope="msg",stripAnsi=False,formatterInstance=None,languageProvider=None, logFile=None,logType="text",logEncoding="utf-8",logForceUTC=False,logIsStream=False,logFormatted=False):
        self.defScope = defaultScope
        self.scope = defaultScope
        self.stripAnsi = stripAnsi

        if logFile != None:
            self.logger = log2File(logFile,logType,logEncoding,logForceUTC,logIsStream)
        else: self.logger = None
        self.logFormatted = logFormatted

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
            orgText = text
            text = f"{color}{title}{reset}{text}{reset}"
            if self.formatterInstance != None:
                text = self.formatterInstance.parse(text,_stripAnsi=self.stripAnsi,addCustomTags=ct)
            if self.logger != None:
                safeTitle = title.replace("[","")
                safeTitle = safeTitle.replace("]: ","")
                safeTitle = safeTitle.replace("]","")
                if self.logFormatted == True:
                    _textToLog = f"{orgText}{reset}"
                    safeTitle = f"{color}{safeTitle}{reset}"
                else:
                    _textToLog = orgText
                self.logger.write(_textToLog,prefix=f"%t {safeTitle}")
            return text
        else:
            reset = self.colors['reset']
            color = self.colors[scope[0]]
            if self.stripAnsi == True:
                reset = ""
                color = ""
            title = ""
            if noPrefix == False:
                title = self.titles[scope[0]]
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
            orgText = text
            text = f"{color}{title}{reset}{text}{reset}"
            if self.formatterInstance != None:
                text = self.formatterInstance.parse(text,_stripAnsi=self.stripAnsi,addCustomTags=ct)
            if self.logger != None:
                safeTitle = title.replace("[","")
                safeTitle = safeTitle.replace("]: ","")
                safeTitle = safeTitle.replace("]","")
                if self.logFormatted == True:
                    _textToLog = f"{orgText}{reset}"
                    safeTitle = f"{color}{safeTitle}{reset}"
                else:
                    _textToLog = orgText
                self.logger.write(_textToLog,prefix=f"%t {safeTitle}")
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
    def enableLogger(self,logFile,logType="text",logEncoding="utf-8",logForceUTC=False,logIsStream=False):
        self.logger = log2File(logFile,logType,logEncoding,logForceUTC,logIsStream)
    def disableLogger(self):
        self.logger = None

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

        self.storage["stateInstances"] = []

        if initOnStart == True:
            self.init()

    def __repr__(self):
        if self.flags.has("--haveBeenInited"):
            return f'<{self.__class__.__module__}.{self.__class__.__name__} object at {hex(id(self))} with id {self.identification} for version {self.regionalGet("VersionData")["versionid"]}>'
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

    def sformat(self,text) -> str:
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        toformat, excludes = exclude_nonToFormat(text)
        formatted = self.getregister("txt").parse(toformat)
        return include_nonToFormat(formatted,excludes)

    def fprint(self,text,file=None,flush=False,end=None,cusPrint=None):
        text = self.sformat(text)
        if cusPrint == None: cusPrint = print
        if end == None:
            cusPrint(text,file=file,flush=flush)
        else:
            cusPrint(text,end=end,file=file,flush=flush)

    def hasUnicodeAvaliable(self):
        return hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() in ['utf-8', 'utf_8', 'utf8']

    def cu_getConSize(self):
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        else:
            if self.flags.has("--hasBeenInited") == True:
                config = self.regionalGet.getProperty("conUtilsConfig")
                ask = config["ask"]
                defW = config["defW"]
                defH = config["defH"]
                asker = config["asker"]
                printer = config["printer"]
                state = config["state"]
                return getConSize(
                    cachePath = state,
                    ask = ask,
                    defW = defW,
                    defH = defH,
                    _asker = asker,
                    _printer = printer
                )
            else:
                return getConSize(
                    cachePath = None,
                    ask = True,
                    defW = 120,
                    defH = 30,
                    _asker = input,
                    _printer = print
                )

    def populateDefaults(self):
        self.flags.enable("--populatedDefaults")

        self.initDefaults["regionalVars"] = {
            "SessionIdentifier": self.identification,
            "DefaultEncoding": "utf-8",
            "RootPathRetrivalMode": "inspect",
            "SettingsReaderMode": "Off",
            "AddPipResolvesToList": False,

            "CSlibDir": None,
            "BaseDir": "{CSlibDir}/..",
            "CoreDir": "{BaseDir}/core",
            "AssetsDir": "{BaseDir}/assets",
            "CacheDir": "{AssetsDir}/cache",
            "PackagesFolder": "{BaseDir}/packages",
            "PackageFilePath": "{PackagesFolder}/.files",
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
            "LangPaths": {
                "AssetsLangPath": "{AssetsDir}/lang",
                "CoreLangPath": "{CoreDir}/lang"
            },
            "LangListFile": "{AssetsDir}/langlist.json",
            "ReaderListFile": "{AssetsDir}/readerlist.json",

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
            "*sformat": self.sformat,
            "SupportsUnicode": self.hasUnicodeAvaliable,

            "AddedPipResolved": [],

            "LangPathObj": None,
            "PkgFilePathObj": None,

            "ReaderRegistry": None,
            "LoadedPackageData": None,

            "PkgFileList": {
                "modulo": [],
                "legacy": []
            },
            "PackageList": {
                "modulo": [],
                "legacy": []
            },

            "conUtilsConfig": {
                "ask": True,
                "defW": 120,
                "defH": 30,
                "asker": input,
                "printer": print,
                "state": "{CacheDir}"
            },

            "__registerAsPaths": [ # __registerAsPaths is used to register the paths as pathTags, so any key in this list will be replaceable, for other keys.
                "CSlibDir","BaseDir","CoreDir","AssetsDir","CacheDir","PackagesFolder","PackageFilePath","mPackPath","lPackPath","ReadersFolder","AssetsLangPath","CoreLangPath"
            ],
            "__registerAsTags": [ # __registerAsTags is used to register additional substituteTags, not usable when initiating regional-vars.
                "DefaultEncoding", "VersionFile","ReaderListFile"
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
            ],
            [
                ["--nomodstm"],
                {
                    "dest": "noModStm",
                    "action": "store_true",
                    "help": "Disables the modularSettings-interface using tagMan by default."
                }
            ],
            [
                ["--fileless"],
                {
                    "dest": "fileless",
                    "action": "store_true",
                    "help": "Makes crosshell attempt to not make files, data will not be static unless session is exported."
                }
            ]
        ]

        self.initDefaults["restArgumentOpts"] = {
            "help": "Unparsed arguments sent to crosshell."
        }

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
                    
                    "Language.Loaded": {"1":"en-us"},
                    "Language._choices": [],
                    "Language.DefaultList": "{CS_LangListFile}",
                    "Language.ListFormat": "json",
                    "Language.LangFormat": "json",
                    "Language.LoadSameSuffixedLangs": True,

                    "conUtilsConfig.ask": True,
                    "conUtilsConfig.defW": 120,
                    "conUtilsConfig.defH": 30,

                    "Packages.Discover.TraverseSymLinks": False,
                    "Packages.Discover.LegacyTraverseDepth": 10,
                    "Packages.AllowedFileTypes.Cmdlets.INTERNAL_PYTHON": ["py"],
                    "Packages.AllowedFileTypes.Packages.Modulo": ["mpackage","mpack","csmpack"],
                    "Packages.AllowedFileTypes.Packages.Legacy": ["package","pack","cspack"],
                    "Packages.Readers.ReaderFile": "{CS_ReaderListFile}",
                    "Packages.Formatting.Mappings.Selected": None,
                    "Packages.Formatting.Mappings._choices": [],
                    "Packages.Formatting.Palettes.Selected": None,
                    "Packages.Formatting.Palettes._choices": [],
                    "CGTS.ANSI_Hex_Palette": "{CS_CGTS_StandardHexPalette}",
                    "CGTS.CustomMappings": {},
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
            "CS_VersionFile": normPathSep(prefixAnyTags(self.initDefaults["regionalVars"]["VersionFile"],self.storage.regionalPrefix)),
            "CS_LangListFile": normPathSep(prefixAnyTags(self.initDefaults["regionalVars"]["LangListFile"],self.storage.regionalPrefix))
        }

        self.initDefaults["startupMessagingConfig"] = {
            "width": 30,
            "incr": "auto",
            "steps": 10,
        }

        self.initDefaults["DefaultVersionData"] = {
            "name": "Crosshell_Modulo",
            "vernr": "Unknown",
            "tags": "Unknown_setByDefault",
            "vid": "Unknown",
            "channel": "Unknown",
            "versionid": 'Crosshell_Modulo:Unknown_Unknown:Unknown'
        }

        self.initDefaults["builtInPkgFeatures"] = {
            "builtin": {
                "readers": {
                    "registeredBy": "builtin",
                    "type": "mapping_1-1",
                    "addr": "/Readers",
                    "legacy_addr": None,
                    "recursive": False,
                    "mangler": readerMangler,
                    "manglerKwargs": {
                        "addMethod": addReader,
                        "readerFile": None,
                        "readerFileEncoding": None,
                        "readerFileIsStream": None
                    }
                },
                "cmdlets": {
                    "registeredBy": "builtin",
                    "type": "registry_forfeature:readers",
                    "addr": "/Cmdlets",
                    "legacy_addr": "/",
                    "recursive": True,
                    "mangler": cmdletMangler,
                    "manglerKwargs": {}
                },
                "mappings": {
                    "registeredBy": "builtin",
                    "type": "raw",
                    "addr": "/Formatting",
                    "legacy_addr": None,
                    "recursive": True
                },
                "palette": {
                    "registeredBy": "builtin",
                    "type": "raw",
                    "addr": "/Formatting",
                    "legacy_addr": None,
                    "recursive": True
                },
                "langpack": {
                    "registeredBy": "builtin",
                    "type": "registry_fortype:json",
                    "addr": "/Langpck",
                    "legacy_addr": None,
                    "recursive": True,
                    "mangler": langpckMangler,
                    "manglerKwargs": {
                        "languageProvider": None,
                        "languagePath": None,
                        "mPackPath": None
                    }
                }
            }
        }

        self.initDefaults["allowedFeatureTypes"] = [
            "mapping_1-1",
            "mapping_1-m",
            "mapping_filen-1",
            "mapping_filen-m",
            "mapping_filep-1",
            "mapping_filep-m",
            "registry_fortype:<type>",
            "registry_forfeature:<feature>",
            "raw"
        ]

        self.initDefaults["defaultReaders"] = {
            "INTERNAL_PYTHON": ["py"]
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

    def createAndReturn_startupW(self,pgMax=10,pgIncr=1,unicodeSymbols=True):
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        return startupMessagingWProgress(
            debugger = self.deb,
            enabled = self.regionalGet("VerboseStart"),
            stripAnsi = self.regionalGet("StripAnsi"),
            pgMax = pgMax,
            pgIncr = pgIncr,
            unicodeSymbols=unicodeSymbols
        )

    def setStripAnsi(self,value=bool):
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        self.regionalSet("StripAnsi",value)
        
    def setVerbStart(self,value=bool):
        if self.flags.has("--enableUnsafeOperations") == False and self.flags.has("--haveBeenInited") == False:
            raise Exception("This operation requires the session to have been inited. `init()`")
        self.regionalSet("VerboseStart",value)

    def init(self, cliArgs=None, regionalVars=None, argumentDeffinionOvw=None, cmdArgPlaceholders=None, pathTagBlacklistKeys=None, additionalSettings=None, additionalPipDeps=None, additionalIngestDefaultTags=None, pipDepsCusPip=None, pipDepsTags=None, launchWith_stripAnsi=False, launchWith_noVerboseStart=False, debug=False,debugFile=None,debugLogType="text",debugForceUTC=False,debugFormatLog=False):
        """Initiates the session."""

        if self.flags.has("--populatedDefaults") == False:
            self.populateDefaults()

        # Enable ansi on windows
        os.system("")

        # [Prepare by getting values]
        # Define standard 
        _regionalVars = self.initDefaults["regionalVars"]

        # Define Arguments
        _arguments = self.initDefaults["arguments"]
        # Define argument placeholders
        _cmdArgPlaceholders = self.initDefaults["cmdArgPlaceholders"]
        # Define pathtagBlackList
        _pathTagBlacklistKeys = self.initDefaults["pathTagBlacklistKeys"]
        # Get peristance/settings defaults
        defaults = self.initDefaults["defaults"]
        # Get pip-dependencies
        pipDeps = self.initDefaults["pipDeps"]
        # Load tags that should be loaded when loading settings/persistance defaults
        _ingestDefaultTags = self.initDefaults["ingestDefaultTags"]
        # Set values based on the method call functions
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
        # Get cliargs
        _cliArgs = cliArgs if cliArgs != None else sys.argv
        _regionalVars["Args"] = _cliArgs

        # [Handle startfile/efile parameters]
        # startfile
        _startfile = "Unknown"
        for i,arg in enumerate(_cliArgs):
            if arg.strip().startswith("@startfile:"):
                __startfile = arg.split("@startfile:")[1] 
                if os.path.exists(__startfile):
                    _startfile = __startfile
                    _cliArgs.pop(i)
                else:
                    _cliArgs[i] = __startfile
        # efile
        if os.path.exists(_cliArgs[0]):
            _efile = _cliArgs[0]
        else:
            _efile = "Unknown"
        # Add them to the temporary regionalVars
        _regionalVars["Startfile"] = _startfile
        _regionalVars["Efile"] = _efile

        # [Get working directories based on the assumption of root/cslib/main.py]
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
        # Add to regionalvars
        _regionalVars["CSlibDir"] = _cslibdir

        # [Evaluate the pathtags in regionalvars for the variables defined in __registerAsPaths]
        tempSubstTagMan = tagSubstitionManager() #init temp-subs-man
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
        # Apply to regionalVars applying blacklist as an exclusionlist
        _regionalVars = _applySubstTags(tempSubstTagMan,_regionalVars,blacklistKeys=_pathTagBlacklistKeys)
        # Add the tags to a dictionary and add that to regionaVars as the baseTags
        initSubstTags = {}
        for key,value in tempSubstTagMan.substTags.items():
            initSubstTags[self.storage.addPrefToKey(key)] = value
        _regionalVars["base_PathTags"] = initSubstTags
        # Clean up
        del tempSubstTagMan

        # [Handle pip dependencies by running them through piptools]
        # handle cuspip
        _pipDepsCusPip = pipDepsCusPip if pipDepsCusPip != None else sys.executable
        _tagMapping = {
            "CusPip": _pipDepsCusPip
        }
        # Additional pip deps?
        if pipDepsTags != None: _tagMapping.update(pipDepsTags)
        # Run through piptools
        resolves = installPipDeps_fl(
            deps = pipDeps,
            tagMapping = _tagMapping,
            returnMods = _regionalVars["AddPipResolvesToList"]
        )
        # if enabled in regionalVars also add to regionalVars
        if _regionalVars["AddPipResolvesToList"] == True:
            _regionalVars["AddedPipResolved"] = resolves
        # cleanup
        del resolves

        # [Handle arguments]
        # Define argparser 
        _argparser = argparse.ArgumentParser(
            **self.initDefaults["argParser_creationKwargs"]
        )
        # Add instance to regionalVars
        _regionalVars["Argparser"] = _argparser
        # Add arguments
        for arg in _arguments:
            _argparser.add_argument(*arg[0], **arg[1])
        # Add argument for additionalInput
        _argparser.add_argument('additional', nargs='*', **self.initDefaults["restArgumentOpts"])

        # Parse args
        _regionalVars["Pargs"] = _argparser.parse_args(_cliArgs)

        # Handle placeholders in command and add stripansi
        cmdIndentifier = self.initDefaults["cmdIdentifier"]
        aliasIndentifiers = self.initDefaults["aliasIdentifiers"]
        seenCmd = False
        seenAliases = []
        self.tmpSet("changedValues",[]) # init temporary list of changed values
        # Iterate over the arguments and replace placeholders for selected values
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
        # Iterate over the arguments and handle aliases for selected keys
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

        # [Add the regionalVars to the session]
        # Append possible custom
        if regionalVars != None: _regionalVars.update(regionalVars)
        # Normalize al paths in values
        _regionalVars = normPathSepObj(_regionalVars)
        # Apply
        self.regionalUpdate(_regionalVars)

        # [Handle Fileless]
        if self.regionalGet("Pargs").fileless == True:
            self.flags.enable("--fileless")
            # add stateInstance to conUtils
            _conUtilsConfig = self.regionalGet("conUtilsConfig")
            _conUtilsConfig["state"] = stateInstance(mode="stream",encoding=self.getEncoding(),parent=self,parentKeepList=self.storage["stateInstances"])
            self.regionalSet("conUtilsConfig",_conUtilsConfig)
        # [Handle launchWith params]
        # Stripansi
        if launchWith_stripAnsi == True:
            self.regionalSet("StripAnsi", True)
            # Append to changedValues temp-list
            __tmp = self.tmpGet("changedValues")
            if "StripAnsi" not in __tmp: __tmp.append("StripAnsi")
            self.tmpSet("changedValues",__tmp)
        # VerboseStart
        if launchWith_noVerboseStart == True:
            self.regionalSet("VerboseStart", False)
            # Append to changedValues temp-list
            __tmp = self.tmpGet("changedValues")
            if "VerboseStart" not in __tmp: __tmp.append("VerboseStart")
            self.tmpSet("changedValues",__tmp)

        # [Register ptm and stm (bases and final collection)]
        # base_ptm (register al tags set as registerAsPaths)
        self.register("base_ptm", pathTagManager(initSubstTags))
        self.getregister("base_ptm").ensureAl() # Ensure pathtags existance
        # base_stm (register al tags set as registerAsTags)
        _substTags = {}
        for k in self.regionalGet("__registerAsTags"):
            if k in _regionalVars.keys():
                _substTags[self.storage.addPrefToKey(k)] = _regionalVars[k]
        self.register("base_stm", tagSubstitionManager(_substTags))
        # Make collectionalTagMan from both the previous
        self.register("stm", collectionalTagManager(initSubstTags,_substTags))
        self.regionalSet("SubstTags", self.getregister("stm").getAlTags() ) # add tags to regionalVars

        # [Make settings and persistance]
        # Handle if the configurators should have stm access (set through argument)
        _setUseTagMan = self.getregister("stm")
        if self.regionalGet("Pargs").noModStm == True: _setUseTagMan = None
        # If fileess make sure there is a stateinstance.stream to write to
        if self.flags.has("--fileless"):
            _isStream = True
            _fileSet = stateInstance(mode="stream",encoding=self.getEncoding(),parent=self,parentKeepList=self.storage["stateInstances"])
            _filePer = stateInstance(mode="stream",encoding=self.getEncoding(),parent=self,parentKeepList=self.storage["stateInstances"])
        else:
            _isStream = False
            _fileSet = self.regionalGet("SettingsFile")
            _filePer = self.regionalGet("PersistanceFile")

        # Make settings object
        self.register("set", modularSettingsLinker(_fileSet,encoding=self.getEncoding(),ensure=True,readerMode=self.regionalGet("SettingsReaderMode"),stm=_setUseTagMan,fileIsStream=_isStream,streamType="yaml"))
        self.getregister("set").createFile() # Incase the linker is using a file ensure its existance
        # Make persistance object
        self.register("per", modularSettingsLinker(_filePer,encoding=self.getEncoding(),ensure=True,readerMode=self.regionalGet("SettingsReaderMode"),stm=_setUseTagMan,fileIsStream=_isStream,streamType="yaml"))
        self.getregister("per").createFile() # Incase the linker is using a file ensure its existance

        # [Populate settings and persistance]
        ## enable allow flag
        self.flags.enable("--enableUnsafeOperations")
        ## Ingest the defaults and the tags that will be allowed for it
        self.ingestDefaults(defaults,_ingestDefaultTags)
        # Get encoding and also set it for both settings/persistance
        self.regionalSet("DefaultEncoding",self.getregister("set").getProperty("crsh","Formats.DefaultEncoding",skipTagMan=False)) # Last time to not use self.getEncoding()
        self.getregister("set").encoding = self.getEncoding()
        self.getregister("per").encoding = self.getEncoding()
        # Handle stripansi/verbosestart so they are applied correctly (Priority of settings,cliargs,launchWith)
        if "StripAnsi" not in self.tmpGet("changedValues"): # Read temp-list
            self.regionalSet("StripAnsi", self.getregister("set").getProperty("crsh","Console.StripAnsi",skipTagMan=True))
        if "VerboseStart" not in self.tmpGet("changedValues"): # Read temp-list
            self.regionalSet("VerboseStart", self.getregister("set").getProperty("crsh","Console.VerboseStart",skipTagMan=True))
        # Remove the temp variable used for storing the changedValues
        self.tmpRemove("changedValues")
        # Load conUtils config from settings instances
        _conUtilsConfig = self.regionalGet("conUtilsConfig")
        _conUtilsConfig["ask"] = self.getregister("set").getProperty("crsh","conUtilsConfig.ask")
        _conUtilsConfig["defW"] = self.getregister("set").getProperty("crsh","conUtilsConfig.defW")
        _conUtilsConfig["defH"] = self.getregister("set").getProperty("crsh","conUtilsConfig.defH")
        # Apply conUtils config from settings instances
        self.regionalSet("conUtilsConfig",_conUtilsConfig)
        # Make startupWprocess from config
        pgMax = self.initDefaults["startupMessagingConfig"]["width"]
        if str(pgMax).lower() == "auto":
            pgMax = getConSize()[0]
        elif str(pgMax).lower().startswith("auto/"):
            div = int(pgMax.split("auto/")[1])
            pgMax = getConSize()[0] // div # roundDown
        pgIncr = self.initDefaults["startupMessagingConfig"]["incr"]
        if str(pgIncr).lower() == "auto":
            steps = self.initDefaults["startupMessagingConfig"]["steps"]
            pgIncr = pgMax // steps # roundDown
        # Make
        st = self.createAndReturn_startupW(
            pgMax = pgMax,
            pgIncr= pgIncr,
            unicodeSymbols = self.regionalGet("SupportsUnicode")()
        )
        # Set scope on debbuger
        self.deb.setScope(
            self.getregister("set").getProperty("crsh_debugger","Scope",skipTagMan=True)
        )
        # if debug is enabled the debugger should log
        if debug == True:
            # Handle log file or if fileless make a stateInstance
            if self.flags.has("--fileless"):
                logFile = stateInstance(mode="stream",encoding=self.getEncoding(),parent=self,parentKeepList=self.storage["stateInstances"])
                _isStream = True
            else:
                _isStream = False
                if debugFile == None:
                    logFile = os.path.join(self.regionalGet("BaseDir"),"debug.log")
                else:
                    logFile = debugFile
            # Enable logger for the debugger using methods
            self.deb.enableLogger(logFile,logType=debugLogType,logEncoding=self.getEncoding(),logForceUTC=debugForceUTC,logIsStream=_isStream)
            self.deb.logFormatted = debugFormatLog
        ## disable allow flag
        self.flags.disable("--enableUnsafeOperations")

        # [Get versionData]
        st.verb("Loading versiondata...") # VERBOSE START

        # Get versionData
        _temp = self.getregister("set").getModule("crsh",skipTagMan=True)
        try:
            # Get from function
            _versionData = crosshellVersionManager_getData(
                versionFile = 
                    self.getregister("stm").eval(
                        mode = "ptm",
                        string = getKeyPath(_temp, "Version.VerFile")
                    ),
                formatVersion = getKeyPath(_temp, "Version.FileFormatVer"),
                encoding = self.getEncoding()
            )
            # Make id
            _versionData["versionid"] = f'{_versionData["name"]}:{_versionData["vernr"]}_{_versionData["channel"]}:{_versionData["vid"]}'
        except:
            # If failed above fallback to defaults
            _versionData = self.initDefaults["DefaultVersionData"]
        # If invalid data also fallback to defaults
        if _versionData == None or _versionData == {}:
            _versionData = self.initDefaults["DefaultVersionData"]
        # Apply to regional
        self.regionalSet("VersionData",_versionData)

        # [Load formatter]
        st.verb("Loading formatter...") # VERBOSE START
        # Get the settings module and use it to get values for CSGT
        _textInst = crosshellGlobalTextSystem(
            pathtagInstance = self.getregister("stm"),
            palette = getKeyPath(_temp,"CGTS.ANSI_Hex_Palette"),
            parseWebcolor = getKeyPath(_temp,"Parse.Text.Webcolors"),
            customTags = getKeyPath(_temp,"CGTS.CustomMappings")
        )
        # Apply stripansi if set in settings
        _textInst.stripAnsi = self.regionalGet("StripAnsi")
        # Apply to regionaGet and the debugger
        self.deb.setFormatterInstance( _textInst )
        self.register("txt", _textInst)
        # Test msg
        st.verb("Does it work? {#DA70D6}*Toad*{r}") # VERBOSE START
        # Apply methods that relly on the formatter
        self.register("fprint",self.regionalGet("fprint"))
        self.register("sformat",self.regionalGet("sformat"))

        # [Init language system]
        # Make a language pathObject and add to regionals
        self.regionalSet(
            "LangPathObj",
            pathObject(
                list(self.regionalGet("LangPaths").values())
            )
        )
        # Handle file for languageList and if fileless make a stateInstance.stream
        if self.flags.has("--fileless"):
            _file = stateInstance(mode="stream",encoding=self.getEncoding(),parent=self,parentKeepList=self.storage["stateInstances"])
            _isStream = True
        else:
            _file = self.getregister("set").getProperty("crsh","Language.DefaultList",skipTagMan=False)
            _isStream = False
        # Init class
        _cslp = crosshellLanguageProvider(
            languageListFile = _file,
            defaultLanguage = self.getregister("set").getProperty("crsh","Language.Loaded",skipTagMan=False),
            listFormat = self.getregister("set").getProperty("crsh","Language.ListFormat",skipTagMan=True),
            langFormat = self.getregister("set").getProperty("crsh","Language.LangFormat",skipTagMan=True),
            pathtagManInstance = self.getregister("stm"),
            langPath = self.regionalGet("LangPathObj"),
            encoding = self.getEncoding(),
            sameSuffixLoading = self.getregister("set").getProperty("crsh","Language.LoadSameSuffixedLangs",skipTagMan=True),
            fileIsStream = _isStream
        )
        # Register and add to debugger
        self.deb.setLanguageProvider(_cslp)
        self.register("lng",_cslp)
        # Test msg
        st.verb(f"Populating languageList... (len: {len(_cslp.languageList)})",l="cs.startup.populanglist._nonadrss_",ct={"len":len(_cslp.languageList)}) # VERBOSE START
        # Call poplulateList to make it aware of the languages present
        _cslp.populateList()
        # Update choices in settings dynamicly
        self.getregister("set").chnProperty("crsh","Language._choices",_cslp.choices)

        # [Handle packages]
        # Start with a pathObj for package files
        _tempPkgFilePath = pathObject([
            self.regionalGet("PackageFilePath")
        ])
        _tempPkgFilePath.ensureAl()
        self.regionalSet("PkgFilePathObj",_tempPkgFilePath)

        # VERBOSE START #
        st.verb("Discovering non-installed packages...",l="cs.startup.discoverpkgs")

        # Retrive a list of packages in /packages
        _tempPkgFileList = self.regionalGet("PkgFileList")
        _installedPackages = {
            "modulo": [],
            "legacy": []
        }
        ## load moduloPackages
        _tempPkgFileList["modulo"],_installedPackages["modulo"] = discoverPackageFiles(
            type_ = "modulo",
            sourcePath = _tempPkgFilePath,
            installDest = self.regionalGet("mPackPath"),
            fileExtensions = handleOSinExtensionsList(
                self.getregister("set").getProperty("crsh","Packages.AllowedFileTypes.Packages.Modulo")
            ),
            excludedFolders = [
                self.regionalGet("lPackPath")
            ],
            travelSymlink = self.getregister("set").getProperty("crsh","Packages.Discover.TraverseSymLinks"),
            moduloEncoding = self.getEncoding()
        )
        ## load legacyPackages
        _tempPkgFileList["legacy"],_installedPackages["legacy"] = discoverPackageFiles(
            type_ = "legacy",
            sourcePath = _tempPkgFilePath,
            installDest = self.regionalGet("lPackPath"),
            fileExtensions = handleOSinExtensionsList(
                self.getregister("set").getProperty("crsh","Packages.AllowedFileTypes.Packages.Legacy")
            ),
            excludedFolders = [
                self.regionalGet("mPackPath")
            ],
            travelSymlink = self.getregister("set").getProperty("crsh","Packages.Discover.TraverseSymLinks"),
            legacyDiscoverTraverseDepth = int(self.getregister("set").getProperty("crsh","Packages.Discover.LegacyTraverseDepth")),
        )
        self.regionalSet("PkgFileList",_tempPkgFileList)
        # VERBOSE START #
        unilen = len([*_tempPkgFileList["legacy"],*_tempPkgFileList["modulo"]])
        if unilen < 1:
            st.verb("Installing {amnt} packages, continuing...",l="cs.startup.installpkgs.zero",ct={"amnt":unilen})
        else:
            st.verb("Found {amnt} non-installed packages...",l="cs.startup.installpkgs",ct={"amnt":unilen})

        # Install any uninstalled package-files, then add to the packageList
        if unilen > 0:
            _installedPackages = installPackageFiles(
                nonInstalledPackages = _tempPkgFileList,
                installedPackages = _installedPackages,
                installDestModulo = self.regionalGet("mPackPath"),
                installDestLegacy = self.regionalGet("lPackPath")
            )
        self.regionalSet("PackageList",_installedPackages)
        
        self.tmpSet("amntPkgsToLoad",len([*_installedPackages["legacy"],*_installedPackages["modulo"]]))

        # clean up
        del unilen
        del _installedPackages
        del _tempPkgFileList
        del _tempPkgFilePath

        # VERBOSE START #
        st.verb("Loading and registring features...",l="cs.startup.loadfeatures")

        # use loadPackageConfig() to get the packageData and features
        packageConfigs,foundFeatures = loadPackageConfig(
            installedPackages = self.regionalGet("PackageList"),
            defaultFeatures = self.initDefaults["builtInPkgFeatures"],
            encoding = self.getEncoding()
        )

        # using the features load in the package featureData
        normFeatureDataAndReg(foundFeatures,self.storage.regFeature,self.initDefaults["allowedFeatureTypes"])

        tempList = []    
        for i in [list(i.keys()) for i in list(foundFeatures.values())]: tempList.extend(i)
        unilen2 = len(tempList)
        del tempList

        # VERBOSE START #
        st.verb("Loading package data... (Pkgs: {amnt}, Features: {amnt2})",l="cs.startup.loadpkgdata",ct={"amnt":self.tmpGet("amntPkgsToLoad"),"amnt2":unilen2})

        # Fill in readerMangler kwargs
        if self.flags.has("--fileless"):
            _readerManglerFile = stateInstance(mode="stream",encoding=self.getEncoding(),parent=self,parentKeepList=self.storage["stateInstances"])
            _readerManglerFileIsStream = True
        else:
            _readerManglerFile = self.getregister("set").getProperty("crsh","Packages.Readers.ReaderFile",skipTagMan=False)
            if os.path.exists(_readerManglerFile) == False:
                if os.path.splitext(_readerManglerFile)[1] == ".json":
                    open(_readerManglerFile,'w',encoding=self.getEncoding()).write("{}")
                else:
                    open(_readerManglerFile,'w',encoding=self.getEncoding()).write("")
            _readerManglerFileIsStream = False
        self.initDefaults["builtInPkgFeatures"]["builtin"]["readers"]["manglerKwargs"] = {
            "addMethod": addReader,
            "readerFile": _readerManglerFile,
            "readerFileEncoding": self.getEncoding(),
            "readerFileIsStream": _readerManglerFileIsStream
        }
        
        # Fill in langpackMangler kwargs
        self.initDefaults["builtInPkgFeatures"]["builtin"]["langpack"]["manglerKwargs"] = {
            "languageProvider": self.getregister("lng"),
            "languagePath": self.regionalGet("LangPathObj"),
            "mPackPath": self.regionalGet("mPackPath")
        }

        # using the loaded features and packageconfigs load package data for the features
        loadedFeatures = loadPackageFeatures(
            loadedFeatures = self.storage.getFeatures(),
            packageConfigs = packageConfigs,
            maxRecursiveDepth = None,
            travelSymlink = False,
            defaultFeatureConfigType = "json",
            mappingFileEncoding = self.getEncoding(),
            preLoadedReaders = self.initDefaults["defaultReaders"],
            preLoadedReadersType = "modulo",
            preLoadedReadersFeature = "readers",
            moduloPackagePath = self.regionalGet("mPackPath"),
            legacyPackagePath = self.regionalGet("lPackPath")
        )

        # Filter cmdlets based on reader-settings
        if loadedFeatures.get("readers"):
            mergedDeffintions = {}
            ## Get a list of al registered filetypes for their reader
            assembledReaderTypes = {}
            for i in list(loadedFeatures["readers"]["data"].values()):
                for i2 in list(i.values()):
                    assembledReaderTypes.update(i2)
            del i,i2
            ## Filter the list based on what types are already in settings (independent of os-selector-prefix)
            settingsDeffinitions = self.getregister("set").getProperty("crsh","Packages.AllowedFileTypes.Cmdlets",skipTagMan=True)
            if self.flags.has("--reBuildSettingReaderTypes") == True:
                for reader,types in settingsDeffinitions.items():
                    # Make a list of types without os-selector-prefix
                    cleanTypes = []
                    for type_ in types:
                        if "@" in type_: type_ = type_.split("@")[1]
                        cleanTypes.append(type_)
                    # Add the list for the reader and add the types from settings
                    mergedDeffintions[reader] = types
                    # Add the new types that wheren't found in the clean list
                    if assembledReaderTypes.get(reader):
                        for type_2 in assembledReaderTypes[reader]:
                            if type_2 not in cleanTypes and type_2 not in types:
                                mergedDeffintions[reader].extend(types)
            else:
                for reader,types in assembledReaderTypes.items():
                    readerName = os.path.basename(reader)
                    if not readerName in settingsDeffinitions.keys():
                        mergedDeffintions[readerName] = types
                    else:
                        mergedDeffintions[readerName] = settingsDeffinitions[readerName]
            ## Update settings with the merged data
            self.getregister("set").chnProperty("crsh","Packages.AllowedFileTypes.Cmdlets",mergedDeffintions)
        else:
            mergedDeffintions = self.getregister("set").getProperty("crsh","Packages.AllowedFileTypes.Cmdlets",skipTagMan=True)

        ## Add the ReaderRegistry with the data from the above
        self.regionalSet("ReaderRegistry",
            toReaderFormat(
                dictFromSettings = mergedDeffintions,
                readerFile = _readerManglerFile,
                encoding = self.getEncoding(),
                isStream = _readerManglerFileIsStream
            )
        )
        del _readerManglerFile,_readerManglerFileIsStream

        # Filter out cmdlets not type-selected
        for packageType,data1 in loadedFeatures["cmdlets"]["data"].items():
            for package,data2 in data1.items():
                for reader,cmdlets in data2.items():
                    validatedCmdlets = []
                    for cmdlet in cmdlets:
                        fileExt = os.path.splitext(cmdlet)[1].lstrip(".")
                        if fileExt in handleOSinExtensionsList(mergedDeffintions[reader]):
                            validatedCmdlets.append(cmdlet)
                    loadedFeatures["cmdlets"]["data"][packageType][package][reader] = validatedCmdlets

        self.regionalSet("LoadedPackageData",loadedFeatures)
        del mergedDeffintions,packageType,data1,package,data2,reader,cmdlets,validatedCmdlets,loadedFeatures

        # VERBOSE START #
        st.verb(f"Preparing for console...",l="cs.startup.preparing-console")

        # Update the palette/mapping choices in settings
        mappingPackages = [i for i in [list(i.keys())[0] if len(i.keys()) > 0 else None for i in list(self.regionalGet("LoadedPackageData")["mappings"]["data"].values())] if i != None]
        palettePackages = [i for i in [list(i.keys())[0] if len(i.keys()) > 0 else None for i in list(self.regionalGet("LoadedPackageData")["palette"]["data"].values())] if i != None]
        self.getregister("set").chnProperty("crsh","Packages.Formatting.Mappings._choices",mappingPackages)
        self.getregister("set").chnProperty("crsh","Packages.Formatting.Palettes._choices",palettePackages)
        
        # Get selected palette/mapping and apply
        selectedMapping = self.getregister("set").getProperty("crsh","Packages.Formatting.Mappings.Selected")
        selectedPalette = self.getregister("set").getProperty("crsh","Packages.Formatting.Palettes.Selected")
        map_of_mappings, map_of_palette = {}, {}
        for p in list(self.regionalGet("LoadedPackageData")["mappings"]["data"].values()): map_of_mappings.update(p)
        for p in list(self.regionalGet("LoadedPackageData")["palette"]["data"].values()): map_of_palette.update(p)
        selectedMappingData = map_of_mappings.get(selectedMapping)
        selectedPaletteData = map_of_palette.get(selectedPalette)
        
        # Apply to text
        if selectedMappingData != None:
            self.getregister("txt").customTags.update(selectedMappingData)
        if selectedPaletteData != None:
            self.getregister("txt").palette.update(selectedPaletteData)

        _tempLng = self.getregister("lng")
        if self.getregister("set").getProperty("crsh","Language.LoadSameSuffixedLangs",skipTagMan=True) == True:
            _tempLng.loadSameSuffixedLanguages()
            _tempLng.load()
            self.getregister("set").chnProperty("crsh","Language.Loaded", _tempLng.languagePrios)
        del _tempLng

        # [Add the default user-vars to storage using self.userVarUpdate()]

        # [Finish up]
        # Set flag
        self.flags.enable("--haveBeenInited")
        # Return
        return self

    def start(self):
        """Starts the set prompt."""
        