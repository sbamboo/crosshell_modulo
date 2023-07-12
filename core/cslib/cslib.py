'''
CSlib functions, can be imported with "import cslib" instead of "from cslib.cslib import *"
'''
# Imports
import subprocess
import sys
import os

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
def crosshellVersionManager_getData(versionFile,formatVersion="1"):
    '''CSlib: gets the versionData from a compatible version file.'''
    data = {}
    if ".yaml" in versionFile:
        import yaml
        data = yaml.loads(open(versionFile,'r').read())
    elif ".json" in versionFile or ".jsonc" in versionFile:
        import json
        data = json.loads(open(versionFile,'r').read())
    forData = data.get("CSverFile")
    verData = data
    if verData.get("CSverFile") != None: verData.pop("CSverFile")
    if int(forData.get("format")) != int(formatVersion):
        raise Exception(f"Invalid format on versionfile, internal '{formatVersion}' whilst external is '{forData.get('format')}'")
    return verData

# Passthrough external libs
from .externalLibs.conUtils import *
from .externalLibs.filesys import filesys
from .datafiles import _fileHandler,getKeyPath,setKeyPath
from ._crosshellParsingEngine import pathtagManager

# Dynamic settings
#TODO: remProperty
class modularSettingsLinker():
    '''CSlib: Links to a settings file to provide a module system'''
    def __init__(self,settingsFile):
        self.file = settingsFile
        self.modules = []
        if ".yaml" in self.file:
            self.filetype = "yaml"
        elif ".json" in self.file or ".jsonc" in self.file or ".json5" in self.file:
            self.filetype = "json"
    def _getContent(self) -> dict:
        data = {}
        if self.filetype == "yaml":
            data = _fileHandler("yaml","get",self.file)
        elif self.filetype == "json":
            data = _fileHandler("json","get",self.file)
        if data == None: data = {}
        return data
    def _setContent(self,content) -> None:
        if self.filetype == "yaml":
            _fileHandler("yaml","set",self.file,content)
        elif self.filetype == "json":
            _fileHandler("json","set",self.file,content)
    def _appendContent(self,content) -> None:
        if self.filetype == "yaml":
            data = _fileHandler("yaml","get",self.file)
            if data == None: data = {}
            data.update(content)
            _fileHandler("yaml","set",self.file,data)
        elif self.filetype == "json":
            data = _fileHandler("json","get",self.file)
            if data == None: data = {}
            data.update(content)
            _fileHandler("json","set",self.file,data)
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
def populateLanguageList(languageListFile,langPath,listFormat="json",langFormat="json",keepExisting=False):
    '''CSlib: Function to populate a language list.'''
    orgLangList = _fileHandler(listFormat,"get",languageListFile)
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
    _fileHandler(listFormat,"set",languageListFile,LangList)

def recheckLangaugeList(languageListFile,listFormat=None,returnDontRemove=False):
    '''CSlib: Checks over a languagelist so al the entries exist, and removses those who don't'''
    if returnDontRemove == True:
        missing = []
    else:
        languageList = _fileHandler(listFormat, "get", languageListFile)
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
        _fileHandler(listFormat, "set", languageListFile, newLanguageList)

class crosshellLanguageProvider():
    '''CSlib: Crosshell language system.'''
    def __init__(self,languageListFile,defaultLanguage="en-us",listFormat="json",langFormat="json",pathtagManInstance=None,langPath=None):
        # Save
        self.languageListFile = languageListFile
        self.defLanguage = self.parseSingleLanguage(defaultLanguage)
        self.listFormat = listFormat
        self.langFormat = langFormat
        self.pathtagManInstance = pathtagManInstance
        self.langPath = langPath
        # Retrive languageList after rechecking it
        recheckLangaugeList(self.languageListFile,self.listFormat)
        self.languageList = _fileHandler(self.listFormat,"get",self.languageListFile)
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
            populateLanguageList(self.languageListFile,self.langPath,self.listFormat,self.langFormat,keepExisting=keepExisting)
            self.relist()
            self.load()
    def relist(self):
        '''Reloads the languageList.'''
        self.languageList = _fileHandler("json","get",self.languageListFile)
    def _load(self,languagelist,language,pathtagManInstance,langFormat):
        if languagelist.get(language) != None:
            if pathtagManInstance == None:
                languageData = _fileHandler(langFormat,"get",languagelist[language])
            else:
                languageData = _fileHandler(langFormat,"get",pathtagManInstance.eval(languagelist[language]))
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
    def print(self,textId,defaultText=None,reloadMode="None"):
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
            if text == None:
                print(defaultText)
            else:
                print(text)
        except:
            print(defaultText)
    def get(self,textId,reloadMode="None"):
        '''Gets a text from the current language, and if needed reloads the language. reloadMode can be 'lang', 'list' or 'both' '''
        if reloadMode == "lang":
            self.load()
        elif reloadMode == "list":
            self.relist()
        elif reloadMode == "both":
            self.relist()
            self.load()
        print(self.languageData.get(textId))



# Class debugger
class crosshellDebugger():
    '''CSlib: Crosshell debugger, this is a text-print based debuggin system.'''
    def __init__(self,defaultDebugMode="limited",stripAnsi=False,formatterInstance=None):
        self.defDebugMode = defaultDebugMode
        self.debugMode = defaultDebugMode
        self.stripAnsi = stripAnsi
        self.allowedModes = ["on","off","limited"]
        self.colors = {"reset":"\033[0m","on":"\033[90m","off":"\033[31m","limited":"\033[90m"}
        #self.colors = {"reset":"\033[0m","on":"\033[90m","off":"\033[31m","limited":"\033[33m"}
        self.formatterInstance = formatterInstance
        self.defFormatterInstance = formatterInstance
    def setDebugMode(self,mode=str):
        if mode not in self.allowedModes:
            raise Exception(f"Mode {mode} is not a debuggerMode, use one of {self.allowedModes}!")
        else:
            self.debugMode = mode
    def resetDebugMode(self):
        self.debugMode = self.defDebugMode
    def setStripAnsi(self,state=bool):
        self.stripAnsi = state
    def setFormatterInstance(self,instance):
        self.formatterInstance = instance
    def resetFormatterInstance(self):
        self.formatterInstance = self.defFormatterInstance
    def print(self,text,onMode="limited"):
        if self.debugMode == onMode:
            reset = self.colors['reset']
            color = self.colors[self.debugMode]
            if self.stripAnsi == True:
                reset = ""
                color = ""
            title = "[CSDebug]: "
            if self.debugMode == "on": title = "[CSDebug<allOutput>]: "
            if self.debugMode == "off": title = "[CSDebug<forcedOutput>]: "
            text = f"{color}{title}{reset}{text}{reset}"
            if self.formatterInstance != None:
                text = self.formatterInstance.parse(text,_stripAnsi=self.stripAnsi)
            print(text)
crshDebug = crosshellDebugger()

# Session
class crosshellSession():
    def __init__(self,sessionFileFormat="json",defaultSessionFile=str):
        self.defSessionFile = defaultSessionFile
        self.sessionFileFormat = sessionFileFormat
        self.sessionFile = self.defSessionFile
        self.loadSessionFile(self.sessionFile)
    def loadSessionFile(self,sessionFile=None):
        if sessionFile == None: sessionFile = self.sessionFile
        self.data = _fileHandler(self.sessionFileFormat, "get", sessionFile)
    def saveSessionFile(self,sessionFile=None):
        if sessionFile == None: sessionFile = self.sessionFile
        _fileHandler(self.sessionFileFormat, "set", sessionFile, self.data)