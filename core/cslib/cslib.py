'''
CSlib functions, can be imported with "import cslib" instead of "from cslib.cslib import *"
'''
# Imports
import subprocess
import sys
import os
import re

# Crossplatform
def normalizePathSep(string) -> str:
    if "\\" in string:
        string = string.replace("\\",os.sep)
    elif "/" in string:
        string = string.replace("/",os.sep)
    return string

def normalizePathSepMT(value):
    if type(value) == str:
        return normalizePathSep(value)
    elif type(value) == list:
        nlist = []
        for item in value:
            nlist.append(normalizePathSep(item))
        return nlist
    elif type(value) == dict:
        ndict ={}
        for key,val in value.items():
            ndict[normalizePathSep(key)] = normalizePathSepMT(val)
        return ndict

# Python
def getExecutingPython() -> str:
    '''CSlib: Returns the path to the python-executable used to start crosshell'''
    return sys.executable

def _check_pip() -> bool:
    '''CSlib_INTERNAL: Checks if PIP is present'''
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call([sys.executable, "-m", "pip", "--version"], stdout=devnull, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False
    return True
def intpip(pip_args):
    '''CSlib: Function to use pip from inside python, this function should also install pip if needed (Experimental)'''
    if not _check_pip():
        print("PIP not found. Installing pip...")
        get_pip_script = "https://bootstrap.pypa.io/get-pip.py"
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip"])
        except subprocess.CalledProcessError:
            print("Failed to install pip using ensurepip. Aborting.")
            return
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        except subprocess.CalledProcessError:
            print("Failed to upgrade pip. Aborting.")
            return
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", get_pip_script])
        except subprocess.CalledProcessError:
            print("Failed to install pip using get-pip.py. Aborting.")
            return
        print("PIP installed successfully.")
    try:
        subprocess.check_call([sys.executable, "-m", "pip"] + pip_args.split())
    except subprocess.CalledProcessError:
        print(f"Failed to execute pip command: {pip_args}")

# crosshellVersionManager
def crosshellVersionManager_getData(versionFile,formatVersion="1",encoding="utf-8"):
    '''CSlib: gets the versionData from a compatible version file.'''
    data = {}
    if ".yaml" in versionFile:
        import yaml
        data = yaml.loads(open(versionFile,'r',encoding=encoding).read())
    elif ".json" in versionFile or ".jsonc" in versionFile:
        import json
        data = json.loads(open(versionFile,'r',encoding=encoding).read())
    forData = data.get("CSverFile")
    verData = data
    if verData.get("CSverFile") != None: verData.pop("CSverFile")
    if int(forData.get("format")) != int(formatVersion):
        raise Exception(f"Invalid format on versionfile, internal '{formatVersion}' whilst external is '{forData.get('format')}'")
    return verData

# Passthrough external libs
from .externalLibs.conUtils import *
from .externalLibs.filesys import filesys
from .datafiles import _fileHandler,getKeyPath,setKeyPath,remKeyPath
from ._crosshellParsingEngine import pathtagManager

# Dynamic settings
#TODO: remProperty
class modularSettingsLinker():
    '''CSlib: Links to a settings file to provide a module system'''
    def __init__(self,settingsFile,encoding="utf-8",ensure=False):
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
    def _getContent(self) -> dict:
        data = {}
        if self.filetype == "yaml":
            data = _fileHandler("yaml","get",self.file,encoding=self.encoding)
        elif self.filetype == "json":
            data = _fileHandler("json","get",self.file,encoding=self.encoding)
        if data == None: data = {}
        return data
    def _setContent(self,content) -> None:
        if self.filetype == "yaml":
            _fileHandler("yaml","set",self.file,content,encoding=self.encoding)
        elif self.filetype == "json":
            _fileHandler("json","set",self.file,content,encoding=self.encoding)
    def _appendContent(self,content) -> None:
        if self.filetype == "yaml":
            data = _fileHandler("yaml","get",self.file,encoding=self.encoding)
            if data == None: data = {}
            data.update(content)
            _fileHandler("yaml","set",self.file,data,encoding=self.encoding)
        elif self.filetype == "json":
            data = _fileHandler("json","get",self.file,encoding=self.encoding)
            if data == None: data = {}
            data.update(content)
            _fileHandler("json","set",self.file,data,encoding=self.encoding)
    def _getModules(self) -> list:
        return list(self._getContent().items())
    def createFile(self,overwrite=False):
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

# Paths
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

# Language
def populateLanguageList(languageListFile,langPath,listFormat="json",langFormat="json",keepExisting=False,encoding="utf-8"):
    '''CSlib: Function to populate a language list.'''
    orgLangList = _fileHandler(listFormat,"get",languageListFile,encoding=encoding)
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
    _fileHandler(listFormat,"set",languageListFile,LangList,encoding=encoding)

def recheckLanguageList(languageListFile,listFormat=None,returnDontRemove=False,encoding="utf-8"):
    '''CSlib: Checks over a languagelist so al the entries exist, and removses those who don't'''
    if returnDontRemove == True:
        missing = []
    else:
        languageList = _fileHandler(listFormat, "get", languageListFile,encoding=encoding)
        newLanguageList = languageList.copy()
    for entry,path in languageList.items():
        if filesys.notExist(path):
            if returnDontRemove == True:
                missing.append({entry:path})
            else:
                newLanguageList.pop(entry)
    if returnDontRemove == True:
        return missing
    else:
        _fileHandler(listFormat, "set", languageListFile, newLanguageList,encoding=encoding)

class crosshellLanguageProvider():
    '''CSlib: Crosshell language system.'''
    def __init__(self,languageListFile,defaultLanguage="en-us",listFormat="json",langFormat="json",pathtagManInstance=None,langPath=None,encoding="utf-8"):
        # Save
        self.languageListFile = languageListFile
        self.defLanguage = self.parseSingleLanguage(defaultLanguage)
        self.listFormat = listFormat
        self.langFormat = langFormat
        self.pathtagManInstance = pathtagManInstance
        self.langPath = langPath
        self.encoding = encoding
        # Retrive languageList after rechecking it
        recheckLanguageList(self.languageListFile,self.listFormat,encoding=self.encoding)
        self.languageList = _fileHandler(self.listFormat,"get",self.languageListFile,encoding=self.encoding)
        # Set default language
        self.languagePrios = defaultLanguage
        self.language = self.defLanguage
        # Load language
        self.load()
    def parseSingleLanguage(self,unparsed):
        if type(unparsed) == str:
            return {"1":unparsed}
        else:
            return unparsed
    def loadLanguagePriorityList(self):
        mergedLanguage = {}
        languages = [value for key, value in sorted(self.languagePrios.items(), key=lambda x: int(x[0]))]
        languages = languages[::-1] # Reverse
        for lang in languages:
            langData = self._load(self.languageList,lang,self.pathtagManInstance,self.langFormat)
            mergedLanguage.update(langData)
        return mergedLanguage
    def populateList(self,keepExisting=False):
        if self.langPath != None:
            populateLanguageList(self.languageListFile,self.langPath,self.listFormat,self.langFormat,keepExisting=keepExisting,encoding=self.encoding)
            self.relist()
            self.load()
    def relist(self):
        '''Reloads the languageList.'''
        self.languageList = _fileHandler("json","get",self.languageListFile,encoding=self.encoding)
    def _load(self,languagelist,language,pathtagManInstance,langFormat):
        if languagelist.get(language) != None:
            if pathtagManInstance == None:
                languageData = _fileHandler(langFormat,"get",languagelist[language],encoding=self.encoding)
            else:
                languageData = _fileHandler(langFormat,"get",pathtagManInstance.eval(languagelist[language]),encoding=self.encoding)
        else:
            languageData = {}
        return languageData
    def load(self):
        '''Retrives the languageFile from the languageList and proceeds to load the language.'''
        self.languageData = self.loadLanguagePriorityList()
    def setLang(self,language):
        '''Set the language.'''
        self.language = self.parseSingleLanguage(language)
        self.load()
    def resLang(self):
        '''Reset the language.'''
        self.language = self.defLanguage.copy()
        self.load()
    def _handleAnsi(self,text):
        return re.sub(r'&(\d+)m', r'\033[\1m', text)
    def _handlePathTags(self,text,extraPathTags=None):
        return self.pathtagManInstance.eval(text,extraPathTags)
    def _handle(self,text,extraPathTags=None):
        if text != None:
            text = self._handleAnsi(text)
            text = self._handlePathTags(text,extraPathTags)
        return text
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

def listInList(sublist,topList):
    founds = {}
    for item in sublist:
        founds[item] = False
    for item in sublist:
        if item in topList:
            founds[item] = True
    founds = list(founds.values())
    if False in founds:
        return False
    else:
        return True

def topPrio(listOfItems,topList):
    indexes = {}
    for item in listOfItems:
        if item in topList:
            indexes[item] = topList.index(item)
    _max = max(list(indexes.values()))
    for item,ind in indexes.items():
        if ind == _max:
            return item


class CrosshellDebErr(Exception):
    def __init__(self, message="The crosshell debugger raised an exception!"):
        self.message = message
        super().__init__(self.message)

class CrosshellExit(Exception):
    def __init__(self, message="Crosshell Exit Exception Raised!"):
        self.message = message
        super().__init__(self.message)

class CrosshellDummy(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__("")

# Class debugger
class crosshellDebugger():
    '''CSlib: Crosshell debugger, this is a text-print based debugging system.'''
    def __init__(self,defaultScope="msg",stripAnsi=False,formatterInstance=None,languageProvider=None):
        self.defScope = defaultScope
        self.scope = defaultScope
        self.stripAnsi = stripAnsi
        # The scopes are are prio listed so if set to 'warn' info and msg will also be shown, to now show set !<mode>
        self.allowedScopes = ["msg","info","warn","error","debug","off"]
        self.colors = {
            "reset":"\033[0m",
            "msg":"",
            "info":"\033[90m",
            "warn":"\033[33m",
            "error":"\033[91m",
            "debug":"\033[90m",
            "off":"\033[31m"
        }
        self.titles = {
            "msg":"[Crsh]: ",
            "info":"[Crsh]: ",
            "warn":"[Crsh<Warn>]: ",
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
            title = self.titles[topScope]
            if type(text) == str:
                text = text.replace(", txt:",",txt:")
                if text.startswith("lng:"):
                    text = text.replace("lng:","")
                    if self.languageProvider != None:
                        _text = self.languageProvider.get(text,lpReloadMode,ct)
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
    def perror(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"error",ct,lpReloadMode,raiseEx,noPrefix)
    def pdebug(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"debug",ct,lpReloadMode,raiseEx,noPrefix)
    def poff(self,text,ct=None,lpReloadMode=None,raiseEx=False,noPrefix=False):
        self.print(text,"off",ct,lpReloadMode,raiseEx,noPrefix)
crshDebug = crosshellDebugger()

# Session
class crosshellSession():
    '''CSlib: Crosshell session, class to contain session data.'''
    def __init__(self,sessionFileFormat="json",defaultSessionFile=str,encoding="utf-8"):
        # Setup
        self.defSessionFile = defaultSessionFile
        self.sessionFileFormat = sessionFileFormat
        self.sessionFile = self.defSessionFile
        self.loadSessionFile(self.sessionFile)
        self.encoding = encoding
        # Variables
        self.registry = {}
        self.data = {}
        self.data["set"] = None
        self.data["lng"] = None
        self.deb = None
        self.varScope = {}
    # Cmdletvariables
    def resetVarScope(self):
        self.varScope = {}
    def setVarScope(self,dict):
        self.varScope = dict
    def uppVarScope(self,dict):
        self.varScope = dict
    def addVarScope(self,key,value):
        self.varScope[key] = value
    def popVarScope(self,key):
        self.varScope.pop(key)
    def getVarScope(self,key=None):
        if key != None:
            return self.varScope[key]
        else:
            return self.varScope
    def joinVarScope(self,scope=dict):
        for key,value in self.varScope.items():
            scope[key] = value
    def uppVarDict(self,scopeDict=dict):
        for key,value in self.varScope.items():
            scopeDict[key] = value
        return scopeDict
    # SessionFiles
    def _handleClassDataGet(self):
        toreturn = self.data.copy()
        if self.data.get("lng") != None:
            toreturn["lng"] = {"languageData":self.data["lng"].languageData,"language":self.data["lng"].language,"languageList":self.data["lng"].languageList,"defLanguage":self.data["lng"].defLanguage}
        if self.data.get("set") != None:
            toreturn["set"] = {"file":self.data["set"].file,"modules":self.data["set"].modules}
        return toreturn
    def _handleClassDataSet(self,data):
        if data == None: data = {}
        try:
            self.data
        except:
            self.data = {}
        if self.data.get("lng") != None:
            self.data["lng"].languageData = data["lng"]["languageData"]
            self.data["lng"].language = data["lng"]["language"]
            self.data["lng"].languageList = data["lng"]["languageList"]
            self.data["lng"].defLanguage = data["lng"]["defLanguage"]
        if self.data.get("set") != None:
            self.data["set"].file = data["set"]["file"]
            self.data["set"].modules = data["set"]["modules"]
    def loadSessionFile(self,sessionFile=None,ovEncoding="utf-8"):
        if sessionFile == None: sessionFile = self.sessionFile
        try:
            enc = self.encoding
        except:
            enc = ovEncoding
        t = _fileHandler(self.sessionFileFormat, "get", sessionFile,encoding=enc)
        self.data = self._handleClassDataSet(t.get("dta"))
        self.registry = t.get("reg")
    def saveSessionFile(self,sessionFile=None,ovEncoding="utf-8"):
        try:
            enc = self.encoding
        except:
            enc = ovEncoding
        if sessionFile == None: sessionFile = self.sessionFile
        _fileHandler(self.sessionFileFormat, "set", sessionFile, {"dta":self._handleClassDataGet(self.data),"reg":self.registry},encoding=enc)
    # Data
    def setSession(self,sessionData=dict):
        '''{"dta":<data>,"reg":<reg>}'''
        self.data = sessionData["dta"]
        self.registry = sessionData["reg"]
    def getSession(self):
        return {"dta":self.data,"reg":self.registry}
    # Registry
    def resetRegistry(self):
        self.registry = {}

def expectedList(value) -> list:
    '''CSlib: Smal function for ensuring lists.'''
    if type(value) != list:
        return [value]
    else:
        return value

def getReaderExecutable(name,readerFile,encoding="utf-8") -> str:
    '''CSlib: Smal function to get the reader-executable from using its name'''
    # get readerFileContent
    readers = _fileHandler("json", "get", readerFile, encoding=encoding, safeSeps=True)
    if readers.get(name) != None:
        return readers.get(name)
    else:
        return None

def addReader(name,execPath,readerFile,encoding="utf-8"):
    '''CSlib: Smal function to add a reader to the readerFile'''
    readers = _fileHandler("json", "get", readerFile, encoding=encoding, safeSeps=True)
    readers[name] = execPath
    _fileHandler("json", "set", readerFile, readers, encoding=encoding)
def remReader(name,readerFile,encoding="utf-8"):
    '''CSlib: Smal function to remove a reader to the readerFile'''
    readers = dict()
    readers = _fileHandler("json", "get", readerFile, encoding=encoding, safeSeps=True)
    readers.pop(name)
    _fileHandler("json", "set", readerFile, readers, encoding=encoding)
def asignReader(settingsInstance,name=str,execPath=str,extensions=list,readerFile=str,encoding="utf-8",baseDictPath="Packages.AllowedFileTypes.Cmdlets"):
    settingsInstance.addProperty("crsh",f"{baseDictPath}.{name}",extensions)
    addReader(name, execPath, readerFile, encoding=encoding)
def usignReader(settingsInstance,name,readerFile,encoding="utf-8"):
    settingsInstance.remProperty("crsh",f"{baseDictPath}.{name}")
    remReader(name, readerFile, encoding=encoding)

def toReaderFormat(dictFromSettings,readerFile,encoding="utf-8") -> list:
    '''CSlib: Smal function for to convert the reader part of settings to the correct format.'''
    readerData = []
    for reader,extensions in dictFromSettings.items():
        readerData.append( {"name":reader,"exec":getReaderExecutable(reader, readerFile, encoding),"extensions":expectedList(extensions)} )
    return readerData

def handleOSinExtensionsList(extensions=list) -> list:
    '''CSlib: Smal function for checking os-specific extensions.'''
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

def getPrefix(csSession,stdPrefix=""):
    # import
    from cslib._crosshellGlobalTextSystem import parsePrefixDirTag
    # Get values
    defprefix = csSession.data["set"].getProperty("crsh","Console.DefPrefix")
    prefix = csSession.data["per"].getProperty("crsh","Prefix")
    prefixEnabled = csSession.data["set"].getProperty("crsh","Console.PrefixEnabled")
    dirEnabled = csSession.data["set"].getProperty("crsh","Console.PrefixShowDir")
    curdir = csSession.data["dir"]
    # Use defprefix if prefix if nto defined
    if prefix == None:
        prefix = defprefix
    # if prefix enabled
    if prefixEnabled != True:
        return stdPrefix
    else:
        # prefix valid?
        if prefix == None:
            return stdPrefix
        # Handle prefix
        else:
            prefix = parsePrefixDirTag(prefix,curdir,dirEnabled,stdPrefix)
            prefix = csSession.data["txt"].parse(prefix)
            prefix = prefix + "\033[0m"
            return prefix

class CmdletVarManager():
    def __init__(self,persistanceInstance,moduleName="CmdletVars",persistent=False):
        self.vars = {}
        self.persistance = persistanceInstance
        self.moduleName=moduleName
        self.persistent = persistent
        self._autocr()
    def _autocr(self):
        if self.moduleName not in self.persistance._getModules() and self.persistent == True:
            self.persistance.addModule(self.moduleName)
    def resper(self):
        if self.persistent == True:
            self.persistance.remModule(self.moduleName)
            self._autocr()
        else:
            self.vars = {}
    def setvar(self,key,value):
        if self.persistent == True:
            self.persistance.addProperty(self.moduleName,key,value)
        else:
            self.vars[key] = value
    def getvar(self,key):
        if self.persistent == True:
            return self.persistance.getProperty(self.moduleName,key)
        else:
            return self.vars.get(key)
    def delvar(self,key):
        if self.persistent == True:
            self.persistance.remProperty(self.moduleName,key)
        else:
            self.vars.pop(key)
    def uppvar(self,key,value):
        if self.persistent == True:
            self.persistance.uppProperty(self.moduleName,key,value)
        else:
            val = self.vars.get(key)
            if type(val) == dict:
                self.vars[key].update(value)
            elif type(val) == list:
                if type(value) == list:
                    self.vars[key].extend(value)
                else:
                    self.vars[key].append(value)
            else:
                self.vars[key] = value
    def chnvar(self,key,value):
        if self.persistent == True:
            self.persistance.chnProperty(self.moduleName,key,value)
        else:
            self.vars[key] = value