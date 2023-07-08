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
class modularSettingsLinker():
    '''CSlib: Links to a settings file to provide a module system'''
    def __init__(self,settingsFile):
        self.file = settingsFile
        self.modules = []
    def _getContent(self) -> dict:
        data = {}
        if ".yaml" in self.file:
            data = _fileHandler("yaml","get",self.file)
        elif ".json" in self.file or ".jsonc" in self.file:
            data = _fileHandler("json","get",self.file)
        if data == None: data = {}
        return data
    def _setContent(self,content) -> None:
        if ".yaml" in self.file:
            _fileHandler("yaml","set",self.file,content)
        elif ".json" in self.file or ".jsonc" in self.file:
            _fileHandler("json","set",self.file,content)
    def _appendContent(self,content) -> None:
        if ".yaml" in self.file:
            data = _fileHandler("yaml","get",self.file)
            if data == None: data = {}
            data.update(content)
            _fileHandler("yaml","set",self.file,data)
        elif ".json" in self.file or ".jsonc" in self.file:
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
    def addPropertie(self,module,keyPath,default,autocreate=False) -> None:
        data = self.get(module,autocreate=autocreate)
        data = setKeyPath(data,keyPath,default)
        self.set(module,data,autocreate=autocreate)
    def getPropertie(self,module,keyPath,autocreate=False) -> None:
        data = self.get(module,autocreate=autocreate)
        return getKeyPath(data,keyPath)

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
    '''CSlib: Function to populate a language list.s'''
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

class crosshellLanguageProvider():
    '''CSlib: Crosshell language system.'''
    def __init__(self,languageListFile,defaultLanguage="en-us",listFormat="json",langFormat="json",pathtagManInstance=None,langPath=None):
        # Save
        self.languageListFile = languageListFile
        self.defLanguage = defaultLanguage
        self.listFormat = listFormat
        self.langFormat = langFormat
        self.pathtagManInstance = pathtagManInstance
        self.langPath = langPath
        # Retrive languageList
        self.languageList = _fileHandler(self.listFormat,"get",self.languageListFile)
        # Set default language
        self.language = defaultLanguage
        # Load language
        self.load()
    def populateList(self,keepExisting=False):
        if self.langPath != None:
            populateLanguageList(self.languageListFile,self.langPath,self.listFormat,self.langFormat,keepExisting=keepExisting)
            self.relist()
            self.load()
    def relist(self):
        '''Reloads the languageList.'''
        self.languageList = _fileHandler("json","get",self.languageListFile)
    def load(self):
        '''Retrives the languageFile from the languageList and proceeds to load the language.'''
        if self.languageList.get(self.language) != None:
            if self.pathtagManInstance == None:
                self.languageData = _fileHandler(self.langFormat,"get",self.languageList[self.language])
            else:
                self.languageData = _fileHandler(self.langFormat,"get",self.pathtagManInstance.eval(self.languageList[self.language]))
        else:
            self.languageData = {}
    def setLang(self,language):
        '''Set the language.'''
        self.language = language
        self.load()
    def resLang(self):
        '''Reset the language.'''
        self.language = self.defLanguage.copy()
        self.load()
    def print(self,textId,defaultText,reloadMode="None"):
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